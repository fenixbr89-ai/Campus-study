"""Small Stripe REST integration without adding another SDK dependency."""
import base64
import hashlib
import hmac
import os
import time
import urllib.parse
import uuid

import httpx

from lib.db import db
from lib.security import decrypt_secret, encrypt_secret, now_utc
from lib.settings import get_settings

STRIPE_API = "https://api.stripe.com/v1"


def _settings_raw(doc: dict) -> dict:
    return doc.get("stripe", {}) if doc else {}


async def get_stripe_config() -> dict:
    doc = await db.settings.find_one({"id": "global"}, {"_id": 0}) or {}
    return _settings_raw(doc)


async def get_public_stripe_config() -> dict:
    cfg = await get_settings()
    stripe = cfg.get("stripe", {})
    return {
        "enabled": bool(stripe.get("enabled")),
        "mode": stripe.get("mode", "test"),
        "publishable_key": stripe.get("publishable_key", ""),
        "monthly_price_id": stripe.get("monthly_price_id", ""),
        "yearly_price_id": stripe.get("yearly_price_id", ""),
        "currency": stripe.get("currency", "BRL"),
        "monthly_price": stripe.get("monthly_price", "19.90"),
        "yearly_price": stripe.get("yearly_price", "150.00"),
        "configured": bool(stripe.get("publishable_key")) and bool(stripe.get("monthly_price_id")) and bool(stripe.get("yearly_price_id")),
    }


async def _secret_key() -> str:
    doc = await db.settings.find_one({"id": "global"}, {"_id": 0, "stripe.secret_key_encrypted": 1}) or {}
    raw = doc.get("stripe", {}).get("secret_key_encrypted", "")
    return decrypt_secret(raw) if raw else ""


async def _webhook_secret() -> str:
    doc = await db.settings.find_one({"id": "global"}, {"_id": 0, "stripe.webhook_secret_encrypted": 1}) or {}
    raw = doc.get("stripe", {}).get("webhook_secret_encrypted", "")
    return decrypt_secret(raw) if raw else ""


async def save_stripe_config(data: dict, *, admin_id: str) -> dict:
    existing = await db.settings.find_one({"id": "global"}, {"_id": 0}) or {}
    old = existing.get("stripe", {})
    stripe = {k: data.get(k, old.get(k, "")) for k in [
        "enabled", "mode", "publishable_key", "monthly_price_id", "yearly_price_id", "currency", "monthly_price", "yearly_price",
    ]}
    if data.get("secret_key"):
        stripe["secret_key_encrypted"] = encrypt_secret(data["secret_key"])
    else:
        stripe["secret_key_encrypted"] = old.get("secret_key_encrypted", "")
    if data.get("webhook_secret"):
        stripe["webhook_secret_encrypted"] = encrypt_secret(data["webhook_secret"])
    else:
        stripe["webhook_secret_encrypted"] = old.get("webhook_secret_encrypted", "")
    await db.settings.update_one({"id": "global"}, {"$set": {"stripe": stripe, "updated_at": now_utc(), "updated_by": admin_id}}, upsert=True)
    return stripe


async def stripe_request(method: str, path: str, data: dict | None = None) -> dict:
    key = await _secret_key()
    if not key:
        raise RuntimeError("Stripe Secret Key não está configurada.")
    headers = {"Authorization": f"Bearer {key}"}
    async with httpx.AsyncClient(timeout=20) as client:
        if method.upper() == "GET":
            res = await client.get(STRIPE_API + path, headers=headers, params=data or {})
        else:
            res = await client.request(method.upper(), STRIPE_API + path, headers=headers, data=data or {})
    if res.status_code >= 400:
        try:
            detail = res.json().get("error", {}).get("message")
        except Exception:
            detail = None
        raise RuntimeError(detail or f"Stripe HTTP {res.status_code}")
    return res.json()


def verify_webhook_signature(raw: bytes, signature_header: str, secret: str, tolerance: int = 300) -> bool:
    if not secret or not signature_header:
        return False
    parts = {}
    for item in signature_header.split(","):
        if "=" in item:
            k, v = item.split("=", 1)
            parts.setdefault(k, []).append(v)
    try:
        timestamp = int(parts.get("t", [""])[0])
    except Exception:
        return False
    if abs(int(time.time()) - timestamp) > tolerance:
        return False
    signed = f"{timestamp}.".encode() + raw
    expected = hmac.new(secret.encode(), signed, hashlib.sha256).hexdigest()
    return any(hmac.compare_digest(expected, value) for value in parts.get("v1", []))


async def create_checkout_session(*, user: dict, plan: str, success_url: str, cancel_url: str) -> str:
    if plan not in {"monthly", "yearly"}:
        raise ValueError("Plano inválido.")
    cfg = await get_stripe_config()
    if not cfg.get("enabled"):
        raise ValueError("O Stripe está desativado no momento.")
    price_id = cfg.get("monthly_price_id") if plan == "monthly" else cfg.get("yearly_price_id")
    if not price_id:
        raise ValueError("Este plano ainda não foi configurado no Stripe.")
    session = await stripe_request("POST", "/checkout/sessions", {
        "mode": "subscription",
        "line_items[0][price]": price_id,
        "line_items[0][quantity]": "1",
        "success_url": success_url,
        "cancel_url": cancel_url,
        "client_reference_id": user["id"],
        "metadata[user_id]": user["id"],
        "metadata[plan]": plan,
        "customer_email": user.get("email", ""),
        "allow_promotion_codes": "true",
    })
    return session["url"]


async def _grant_from_subscription(subscription_id: str, user_id: str, plan: str, status: str, current_period_end: int | None = None) -> None:
    expiry = None
    if current_period_end:
        from datetime import datetime, timezone
        expiry = datetime.fromtimestamp(current_period_end, timezone.utc)
    existing = await db.access_grants.find_one({"user_id": user_id, "feature": "premium"}, {"_id": 0})
    doc = {
        "id": existing.get("id", str(uuid.uuid4())) if existing else str(uuid.uuid4()),
        "user_id": user_id, "feature": "premium", "enabled": status in {"active", "trialing", "past_due"},
        "expires_at": expiry, "source": "stripe", "subscription_id": subscription_id, "plan": plan,
        "updated_at": now_utc(),
    }
    if existing:
        await db.access_grants.replace_one({"user_id": user_id, "feature": "premium"}, doc)
    else:
        await db.access_grants.insert_one(doc)


async def process_webhook_event(event: dict) -> None:
    event_type = event.get("type", "")
    obj = event.get("data", {}).get("object", {})
    if event_type == "checkout.session.completed":
        user_id = obj.get("metadata", {}).get("user_id") or obj.get("client_reference_id")
        subscription_id = obj.get("subscription")
        plan = obj.get("metadata", {}).get("plan", "monthly")
        if user_id and subscription_id:
            sub = await stripe_request("GET", f"/subscriptions/{subscription_id}")
            await _grant_from_subscription(subscription_id, user_id, plan, sub.get("status", "active"), sub.get("current_period_end"))
            await db.stripe_subscriptions.update_one(
                {"subscription_id": subscription_id},
                {"$set": {"subscription_id": subscription_id, "user_id": user_id, "plan": plan, "status": sub.get("status", "active"), "current_period_end": sub.get("current_period_end"), "updated_at": now_utc()}, "$setOnInsert": {"created_at": now_utc()}},
                upsert=True,
            )
    elif event_type in {"customer.subscription.created", "customer.subscription.updated", "customer.subscription.deleted", "customer.subscription.paused", "customer.subscription.resumed"}:
        sub_id = obj.get("id")
        rec = await db.stripe_subscriptions.find_one({"subscription_id": sub_id}, {"_id": 0}) if sub_id else None
        user_id = rec.get("user_id") if rec else obj.get("metadata", {}).get("user_id")
        plan = rec.get("plan", "monthly") if rec else obj.get("metadata", {}).get("plan", "monthly")
        if sub_id and user_id:
            status = obj.get("status", "canceled")
            await _grant_from_subscription(sub_id, user_id, plan, status, obj.get("current_period_end"))
            await db.stripe_subscriptions.update_one({"subscription_id": sub_id}, {"$set": {"user_id": user_id, "plan": plan, "status": status, "current_period_end": obj.get("current_period_end"), "updated_at": now_utc()}, "$setOnInsert": {"created_at": now_utc()}}, upsert=True)
    elif event_type in {"invoice.payment_succeeded", "invoice.paid", "invoice.payment_failed"}:
        subscription_id = obj.get("subscription")
        if subscription_id:
            rec = await db.stripe_subscriptions.find_one({"subscription_id": subscription_id}, {"_id": 0})
            if rec and rec.get("user_id"):
                sub = await stripe_request("GET", f"/subscriptions/{subscription_id}")
                status = sub.get("status", rec.get("status", "past_due"))
                await _grant_from_subscription(subscription_id, rec["user_id"], rec.get("plan", "monthly"), status, sub.get("current_period_end"))
                await db.stripe_subscriptions.update_one({"subscription_id": subscription_id}, {"$set": {"status": status, "current_period_end": sub.get("current_period_end"), "updated_at": now_utc()}})

"""Stripe checkout/subscription endpoints."""
from fastapi import APIRouter, Depends, HTTPException, Request
from lib.auth import current_user
from lib.db import db
from lib.security import now_utc
from lib.stripe import create_checkout_session, get_public_stripe_config, get_stripe_config, process_webhook_event, verify_webhook_signature, stripe_request
from models.schemas import StripeCheckoutIn, StripeCheckoutOut, StripeWebhookResult

router = APIRouter(prefix="/payments/stripe", tags=["payments"])

@router.get("/config")
async def stripe_config():
    return await get_public_stripe_config()

@router.post("/checkout", response_model=StripeCheckoutOut)
async def stripe_checkout(body: StripeCheckoutIn, user: dict = Depends(current_user)):
    request_origin = None
    # The frontend sends absolute URLs when possible. These defaults work on Vercel deployments too.
    # Environment variables can override them so local/staging does not need code changes.
    import os
    base = os.environ.get("PUBLIC_APP_URL", "").rstrip("/")
    if not base:
        raise HTTPException(500, "Configure PUBLIC_APP_URL no backend antes de ativar o checkout.")
    try:
        url = await create_checkout_session(user=user, plan=body.plan, success_url=f"{base}/checkout?sucesso=1", cancel_url=f"{base}/checkout?cancelado=1")
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(502, str(exc)) from exc
    return StripeCheckoutOut(url=url)

@router.post("/webhook", response_model=StripeWebhookResult)
async def stripe_webhook(request: Request):
    raw = await request.body()
    signature = request.headers.get("Stripe-Signature", "")
    secret = (await get_stripe_config()).get("webhook_secret_encrypted", "")
    from lib.security import decrypt_secret
    secret = decrypt_secret(secret) if secret else ""
    if not verify_webhook_signature(raw, signature, secret):
        raise HTTPException(400, "Assinatura do webhook do Stripe inválida.")
    try:
        event = await request.json()
    except Exception as exc:
        raise HTTPException(400, "Webhook inválido.") from exc
    event_id = event.get("id", "")
    if not event_id:
        raise HTTPException(400, "Webhook sem identificador.")
    if await db.stripe_events.find_one({"event_id": event_id}):
        return StripeWebhookResult(event_id=event_id)
    try:
        await process_webhook_event(event)
    except RuntimeError as exc:
        raise HTTPException(502, str(exc)) from exc
    await db.stripe_events.insert_one({"event_id": event_id, "type": event.get("type", ""), "at": now_utc()})
    return StripeWebhookResult(event_id=event_id)

"""Global platform settings — one document in db.settings."""
import os
from lib.db import db

def stripe_defaults() -> dict:
    return {
        "enabled": False, "mode": "test", "publishable_key": "",
        "secret_key_encrypted": "", "monthly_price_id": "", "yearly_price_id": "",
        "currency": "BRL", "monthly_price": "19.90", "yearly_price": "150.00",
        "webhook_secret_encrypted": "",
    }

def feature_defaults() -> dict:
    return {
        "limitado": {"pdf": True, "videoaulas": True, "materiais": False, "artigos": True, "questoes": False, "simulados": False, "campus_ai": True, "ranking": True, "anotacoes": True, "favoritos": True, "relatorios": True, "benefit_labels": []},
        "ilimitado": {"pdf": True, "videoaulas": True, "materiais": True, "artigos": True, "questoes": True, "simulados": True, "campus_ai": True, "ranking": True, "anotacoes": True, "favoritos": True, "relatorios": True, "benefit_labels": []},
    }

def _defaults() -> dict:
    return {
        "platform_name": os.environ.get("PLATFORM_NAME", "Campus Study"),
        "support_email": os.environ.get("SUPPORT_EMAIL", "suporte@campusstudy.com"),
        "default_daily_goal_minutes": 60,
        "allow_registration": True,
        "stripe": stripe_defaults(),
        "features": feature_defaults(),
    }

async def get_settings() -> dict:
    doc = await db.settings.find_one({"id": "global"}, {"_id": 0}) or {}
    merged = {**_defaults(), **doc}
    merged["stripe"] = {**stripe_defaults(), **doc.get("stripe", {})}
    merged["stripe"].pop("secret_key_encrypted", None)
    merged["stripe"].pop("webhook_secret_encrypted", None)
    merged["stripe"]["secret_key"] = ""
    merged["stripe"]["webhook_secret"] = ""
    merged["stripe"]["secret_key_configured"] = bool(doc.get("stripe", {}).get("secret_key_encrypted"))
    merged["stripe"]["webhook_secret_configured"] = bool(doc.get("stripe", {}).get("webhook_secret_encrypted"))
    defaults = feature_defaults()
    merged["features"] = {**defaults, **doc.get("features", {})}
    legacy = doc.get("features", {})
    legacy_limited = legacy.get("free", {})
    legacy_unlimited = legacy.get("premium", {})
    merged["features"]["limitado"] = {**defaults["limitado"], **legacy_limited, **legacy.get("limitado", {})}
    merged["features"]["ilimitado"] = {**defaults["ilimitado"], **legacy_unlimited, **legacy.get("ilimitado", {})}
    merged.setdefault("updated_at", None)
    merged.setdefault("updated_by", "")
    return merged

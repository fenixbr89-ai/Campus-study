"""Authentication and role dependencies for the Campus Study platform."""

from datetime import timedelta
from fastapi import Depends, HTTPException, Request

from lib.db import db
from lib.security import SESSION_COOKIE, decode_session_token, now_utc, aware

STAFF_ROLES = {"admin", "superadmin", "editor", "moderator"}


async def optional_user(request: Request) -> dict | None:
    token = request.cookies.get(SESSION_COOKIE)
    if not token:
        return None
    payload = decode_session_token(token)
    if not payload:
        return None
    user = await db.users.find_one({"id": payload["sub"]}, {"_id": 0})
    if not user or user.get("token_version", 0) != payload.get("tv") or user.get("status") == "bloqueado":
        return None
    user = await ensure_trial(user)
    user["_access_grants"] = await db.access_grants.find({"user_id": user["id"], "expires_at": {"$gt": now_utc()}}, {"_id": 0}).to_list(100)
    settings = await db.settings.find_one({"id": "global"}, {"_id": 0, "features": 1}) or {}
    default_features = {
        "limitado": {"pdf": True, "videoaulas": True, "materiais": True, "artigos": True, "questoes": False, "simulados": False, "campus_ai": True, "ranking": True, "anotacoes": True, "favoritos": True, "relatorios": True},
        "ilimitado": {"pdf": True, "videoaulas": True, "materiais": True, "artigos": True, "questoes": True, "simulados": True, "campus_ai": True, "ranking": True, "anotacoes": True, "favoritos": True, "relatorios": True},
    }
    user["_feature_settings"] = {**default_features, **settings.get("features", {})}
    user["_feature_settings"]["limitado"] = {**default_features["limitado"], **settings.get("features", {}).get("limitado", {})}
    user["_feature_settings"]["ilimitado"] = {**default_features["ilimitado"], **settings.get("features", {}).get("ilimitado", {})}
    return user


async def current_user(user: dict | None = Depends(optional_user)) -> dict:
    if not user:
        raise HTTPException(401, "Faça login para continuar.")
    return user


async def admin_user(user: dict = Depends(current_user)) -> dict:
    if user.get("role") not in ("admin", "superadmin"):
        raise HTTPException(403, "Acesso restrito à administração.")
    return user



async def log_admin(admin: dict, action: str, entity: str, entity_id: str = "") -> None:
    import uuid

    await db.admin_logs.insert_one({
        "id": str(uuid.uuid4()), "admin_id": admin["id"], "admin_name": admin["name"],
        "action": action, "entity": entity, "entity_id": entity_id, "at": now_utc(),
    })


TRIAL_DAYS = 30
PREMIUM_FEATURES = {"plataforma", "premium", "todos"}

async def ensure_trial(user: dict) -> dict:
    """Guarantee every student has a 30-day launch trial, including legacy accounts."""
    if user.get("trial_started_at"):
        return user
    started = now_utc()
    ends = started + timedelta(days=TRIAL_DAYS)
    await db.users.update_one({"id": user["id"]}, {"$set": {"trial_started_at": started, "trial_ends_at": ends}})
    user["trial_started_at"], user["trial_ends_at"] = started, ends
    return user

def has_premium(user: dict) -> bool:
    if user.get("role") in STAFF_ROLES:
        return True
    now = now_utc()
    for grant in user.get("_access_grants", []):
        expires_at = aware(grant.get("expires_at"))
        if grant.get("feature") in PREMIUM_FEATURES and expires_at and expires_at > now:
            return True
    return False

def trial_active(user: dict) -> bool:
    ends = aware(user.get("trial_ends_at"))
    if not ends:
        return True
    return ends > now_utc()

def full_access(user: dict) -> bool:
    override = user.get("admin_plan")
    if override == "ilimitado":
        return True
    if override == "limitado":
        return trial_active(user) or has_premium(user)
    return trial_active(user) or has_premium(user)

def require_feature_access(user: dict, feature: str) -> None:
    # Staff mantém acesso total. Durante o período de avaliação, o plano segue as regras Premium.
    plan = "ilimitado" if full_access(user) else "limitado"
    features = user.get("_feature_settings", {}).get(plan, {})
    if features.get(feature, True):
        return
    raise HTTPException(403, f"{feature.capitalize()} não está disponível no seu plano atual.")

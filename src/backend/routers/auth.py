import os
import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile

from lib.auth import current_user, ensure_trial, has_premium, trial_active
from lib.db import db
from lib.email import reset_email_html, send_email
from lib.security import (
    SESSION_COOKIE, SESSION_DAYS, aware, create_session_token, digest_token,
    hash_password, new_reset_token, now_utc, rate_limit, validate_password_strength, verify_password,
)
from models.schemas import AdminLoginIn, ChangePasswordIn, DeleteAccountIn, ForgotIn, LoginIn, Me, Message, ProfileIn, RegisterIn, ResetIn

router = APIRouter(prefix="/auth", tags=["auth"])
RESET_MINUTES = 30
TERMS_VERSION = os.environ.get("TERMS_VERSION", "1.0")
PRIVACY_VERSION = os.environ.get("PRIVACY_VERSION", "1.0")


def _ip(request: Request) -> str:
    return (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "")).split(",")[0].strip()


def _set_cookie(response: Response, user: dict) -> None:
    secure_cookie = os.environ.get("COOKIE_SECURE", "true").lower() not in {"0", "false", "no"}
    response.set_cookie(SESSION_COOKIE, create_session_token(user["id"], user.get("token_version", 0)),
                        max_age=SESSION_DAYS * 86400, httponly=True, secure=secure_cookie, samesite="lax", path="/")


def to_me(user: dict) -> Me:
    trial_start = aware(user.get("trial_started_at") or user.get("created_at"))
    trial_end = aware(user.get("trial_ends_at"))
    if trial_end is None and trial_start is not None:
        trial_end = trial_start + timedelta(days=30)
    now = now_utc()
    active = bool(trial_end and trial_end > now)
    premium = has_premium(user)
    days = max(0, (trial_end - now).days + (1 if trial_end and (trial_end - now).seconds else 0)) if active else 0
    return Me(**{**user, "trial_started_at": trial_start,
                 "trial_ends_at": trial_end, "plan": "premium" if premium else "free",
                 "trial_active": active, "trial_days_left": days})


@router.post("/register", response_model=Me)
async def register(body: RegisterIn, request: Request, response: Response):
    rate_limit(f"register:{_ip(request)}", 10, 3600)
    from lib.settings import get_settings
    settings = await get_settings()
    if not settings.get("allow_registration", True):
        raise HTTPException(403, "O cadastro de novas contas está temporariamente desativado. Tente novamente mais tarde.")
    if body.password != body.password_confirm:
        raise HTTPException(400, "As senhas não coincidem.")
    validate_password_strength(body.password)
    if not (body.accept_terms and body.accept_privacy):
        raise HTTPException(400, "É necessário aceitar os Termos de Uso e a Política de Privacidade.")
    email = body.email.lower()
    if await db.users.find_one({"email": email}):
        raise HTTPException(409, "Este e-mail já está em uso por outra conta.")
    now = now_utc()
    user = {
        "id": str(uuid.uuid4()), "name": body.name.strip(), "email": email,
        "password_hash": hash_password(body.password),
        "role": "student", "status": "ativo", "token_version": 0,
        "daily_goal_minutes": settings.get("default_daily_goal_minutes", 60),
        "course_id": None, "faculty": "", "avatar_url": "", "ranking_opt_in": True, "created_at": now, "last_login_at": now,
        "terms_version": TERMS_VERSION, "privacy_version": PRIVACY_VERSION,
        "terms_accepted_at": now, "privacy_accepted_at": now,
        "trial_started_at": now, "trial_ends_at": now + timedelta(days=30),
    }
    await db.users.insert_one(user)
    _set_cookie(response, user)
    return to_me(user)


@router.post("/login", response_model=Me)
async def login(body: LoginIn, request: Request, response: Response):
    rate_limit(f"login:{_ip(request)}", 20, 600)
    rate_limit(f"login-email:{body.email.lower()}", 8, 600)
    user = await db.users.find_one({"email": body.email.lower()}, {"_id": 0})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "E-mail ou senha incorretos.")
    if user.get("status") == "bloqueado":
        raise HTTPException(403, "Sua conta está bloqueada. Entre em contato com o suporte.")
    await db.users.update_one({"id": user["id"]}, {"$set": {"last_login_at": now_utc()}})
    _set_cookie(response, user)
    return to_me(user)


@router.post("/logout", response_model=Message)
async def logout(response: Response):
    secure_cookie = os.environ.get("COOKIE_SECURE", "true").lower() not in {"0", "false", "no"}
    response.delete_cookie(SESSION_COOKIE, path="/", secure=secure_cookie, httponly=True, samesite="lax")
    return Message(message="Sessão encerrada.")


@router.post("/admin-login", response_model=Me)
async def admin_login(body: AdminLoginIn, request: Request, response: Response):
    """Login exclusivo da equipe usando e-mail + senha."""
    rate_limit(f"admin-login:{_ip(request)}", 20, 600)
    rate_limit(f"admin-login-email:{body.email.lower()}", 8, 600)
    user = await db.users.find_one({"email": body.email.lower()}, {"_id": 0})
    if not user or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(401, "E-mail ou senha incorretos.")
    if user.get("role") not in ("admin", "superadmin"):
        raise HTTPException(403, "Acesso restrito à administração.")
    if user.get("status") == "bloqueado":
        raise HTTPException(403, "Sua conta está bloqueada.")
    await db.users.update_one({"id": user["id"]}, {"$set": {"last_login_at": now_utc()}})
    _set_cookie(response, user)
    return to_me(user)


@router.get("/me", response_model=Me)
async def me(user: dict = Depends(current_user)):
    return to_me(user)


@router.put("/profile", response_model=Me)
async def update_profile(body: ProfileIn, user: dict = Depends(current_user)):
    payload = body.model_dump()
    if payload.get("course_id"):
        course = await db.courses.find_one({"id": payload["course_id"], "status": "publicado"}, {"id": 1})
        if not course:
            raise HTTPException(400, "Curso selecionado não está disponível.")
    changed = [field for field in ("name", "daily_goal_minutes", "course_id", "faculty", "ranking_opt_in") if user.get(field) != payload.get(field)]
    await db.users.update_one({"id": user["id"]}, {"$set": payload})
    user.update(payload)
    if changed:
        await db.history.insert_one({"id": str(uuid.uuid4()), "user_id": user["id"], "event_kind": "perfil",
                                     "at": now_utc(), "topic_id": "", "topic_name": "", "discipline_name": "",
                                     "course_name": "", "path": "/perfil", "task_title": "Atualização do perfil"})
    return to_me(user)

@router.post("/profile/photo")
async def update_profile_photo(file: UploadFile = File(...), user: dict = Depends(current_user)):
    allowed = {"image/jpeg", "image/png", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(400, "Use uma imagem JPG, PNG ou WebP.")
    data = await file.read()
    if len(data) > 5 * 1024 * 1024:
        raise HTTPException(413, "A foto excede o limite de 5 MB.")
    from motor.motor_asyncio import AsyncIOMotorGridFSBucket
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="campus_files")
    fid = await bucket.upload_from_stream(file.filename or "avatar", data, metadata={"content_type": file.content_type, "purpose": "avatar", "user_id": user["id"]})
    url = f"/api/uploads/{fid}"
    await db.users.update_one({"id": user["id"]}, {"$set": {"avatar_url": url}})
    return {"avatar_url": url}


GENERIC_FORGOT = ("Se o e-mail estiver cadastrado, enviamos um link de redefinição para o endereço informado. "
                  "Verifique sua caixa de entrada e o spam.")


@router.post("/forgot-password", response_model=Message)
async def forgot_password(body: ForgotIn, request: Request):
    rate_limit(f"forgot:{_ip(request)}", 5, 900)
    user = await db.users.find_one({"email": body.email.lower()}, {"_id": 0})
    if user and user.get("status") != "bloqueado":
        raw, digest = new_reset_token()
        await db.password_resets.update_many({"user_id": user["id"], "used": False}, {"$set": {"used": True}})
        await db.password_resets.insert_one({
            "id": str(uuid.uuid4()), "user_id": user["id"], "token_hash": digest, "used": False,
            "created_at": now_utc(), "expires_at": now_utc() + timedelta(minutes=RESET_MINUTES),
        })
        public_app = os.environ.get("PUBLIC_APP_URL", "").rstrip("/")
        if public_app:
            link = f"{public_app}/redefinir-senha?token={raw}"
        else:
            host = request.headers.get("x-forwarded-host") or request.headers.get("host", "")
            scheme = "http" if host.startswith(("localhost", "127.0.0.1")) else "https"
            link = f"{scheme}://{host}/redefinir-senha?token={raw}"
        await send_email(to=user["email"], subject="Redefinição de senha — Campus Study",
                         html=reset_email_html(user["name"], link, RESET_MINUTES))
    return Message(message=GENERIC_FORGOT)


@router.get("/reset-password/validate", response_model=Message)
async def validate_reset(token: str):
    rec = await db.password_resets.find_one({"token_hash": digest_token(token)})
    if not rec or rec["used"] or aware(rec["expires_at"]) < now_utc():
        raise HTTPException(400, "Este link é inválido, já foi utilizado ou expirou. Solicite um novo.")
    return Message(message="Link válido.")


@router.post("/reset-password", response_model=Message)
async def reset_password(body: ResetIn, request: Request):
    rate_limit(f"reset:{_ip(request)}", 10, 900)
    if body.password != body.password_confirm:
        raise HTTPException(400, "As senhas não coincidem.")
    validate_password_strength(body.password)
    rec = await db.password_resets.find_one_and_update(
        {"token_hash": digest_token(body.token), "used": False, "expires_at": {"$gt": now_utc()}},
        {"$set": {"used": True, "used_at": now_utc()}},
    )
    if not rec:
        raise HTTPException(400, "Este link é inválido, já foi utilizado ou expirou. Solicite um novo.")
    await db.users.update_one({"id": rec["user_id"]}, {"$set": {"password_hash": hash_password(body.password)},
                                                       "$inc": {"token_version": 1}})
    return Message(message="Senha atualizada com sucesso! Entre com sua nova senha.")


@router.post("/change-password", response_model=Message)
async def change_password(body: ChangePasswordIn, request: Request, user: dict = Depends(current_user)):
    rate_limit(f"change-password:{_ip(request)}:{user['id']}", 8, 900)
    if not verify_password(body.current_password, user["password_hash"]):
        raise HTTPException(401, "A senha atual está incorreta.")
    if body.new_password != body.new_password_confirm:
        raise HTTPException(400, "As novas senhas não coincidem.")
    if verify_password(body.new_password, user["password_hash"]):
        raise HTTPException(400, "A nova senha deve ser diferente da senha atual.")
    validate_password_strength(body.new_password)
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"password_hash": hash_password(body.new_password)}, "$inc": {"token_version": 1}},
    )
    return Message(message="Senha alterada. Entre novamente para continuar.")


@router.get("/data-export")
async def export_personal_data(user: dict = Depends(current_user)):
    """LGPD data portability endpoint. Exposes only the authenticated user's own data."""
    collections = ("users", "favorites", "history", "progress", "daily_stats", "study_sessions",
                   "exams", "exam_plans", "exam_tasks", "question_reviews", "topic_favorites", "user_items",
                   "notes", "submissions", "notifications", "support_tickets", "user_achievements", "access_grants")
    result = {}
    for name in collections:
        rows = await db[name].find({"user_id": user["id"]}, {"_id": 0}).to_list(5000)
        if name == "users":
            rows = [{k: v for k, v in user.items() if k not in {"password_hash", "cpf_hash", "_access_grants", "_feature_settings"}}]
        result[name] = rows
    result["exported_at"] = now_utc().isoformat()
    result["privacy_note"] = "Exportação dos dados associados à conta autenticada."
    return result


@router.post("/delete-account", response_model=Message)
async def delete_account(body: DeleteAccountIn, response: Response, user: dict = Depends(current_user)):
    if body.confirmation != "EXCLUIR MINHA CONTA":
        raise HTTPException(400, "Confirmação inválida.")
    if not verify_password(body.current_password, user["password_hash"]):
        raise HTTPException(401, "A senha atual está incorreta.")
    uid = user["id"]
    # Keep the deletion allowlist explicit: only user-owned collections are touched.
    collections = ("favorites", "history", "progress", "daily_stats", "study_sessions",
                   "exams", "exam_plans", "exam_tasks", "question_reviews", "topic_favorites", "user_items",
                   "notes", "submissions", "notifications", "support_tickets", "user_achievements", "access_grants")
    for name in collections:
        await db[name].delete_many({"user_id": uid})
    # Remove password reset tokens and the account itself; token_version becomes irrelevant after deletion.
    await db.password_resets.delete_many({"user_id": uid})
    try:
        from motor.motor_asyncio import AsyncIOMotorGridFSBucket
        from bson import ObjectId
        bucket = AsyncIOMotorGridFSBucket(db, bucket_name="campus_files")
        async for f in db["campus_files.files"].find({"metadata.user_id": uid}, {"_id": 1}):
            await bucket.delete(f["_id"])
    except Exception:
        # Account deletion remains valid even if an old avatar cannot be cleaned up.
        pass
    deleted = await db.users.delete_one({"id": uid})
    if deleted.deleted_count != 1:
        raise HTTPException(404, "Conta não encontrada.")
    secure_cookie = os.environ.get("COOKIE_SECURE", "true").lower() not in {"0", "false", "no"}
    response.delete_cookie(SESSION_COOKIE, path="/", secure=secure_cookie, httponly=True, samesite="lax")
    return Message(message="Conta excluída com sucesso.")

"""Security helpers: CPF validation/hashing, password hashing, JWT sessions, rate limiting."""

import hashlib
import hmac
import os
import re
import secrets
import time
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from fastapi import HTTPException

JWT_SECRET = os.environ["JWT_SECRET"]
CPF_PEPPER = os.environ.get("CPF_PEPPER", "legacy-disabled")
SESSION_COOKIE = "cs_session"
SESSION_DAYS = 14


def only_digits(value: str) -> str:
    return re.sub(r"\D", "", value or "")


def is_valid_cpf(value: str) -> bool:
    cpf = only_digits(value)
    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False
    for size in (9, 10):
        total = sum(int(cpf[i]) * (size + 1 - i) for i in range(size))
        digit = (total * 10) % 11
        if digit == 10:
            digit = 0
        if digit != int(cpf[size]):
            return False
    return True


def cpf_hash(value: str) -> str:
    """Keyed hash (HMAC-SHA256) — CPF is never stored in plain text."""
    return hmac.new(CPF_PEPPER.encode(), only_digits(value).encode(), hashlib.sha256).hexdigest()


def cpf_masked(value: str) -> str:
    d = only_digits(value)
    return f"***.{d[3:6]}.***-**"


def mask_email(email: str) -> str:
    name, _, domain = email.partition("@")
    return f"{name[:2]}***@{domain}"


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12)).decode()


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except ValueError:
        return False


def validate_password_strength(password: str) -> None:
    if len(password) < 8 or not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise HTTPException(400, "A senha deve ter pelo menos 8 caracteres, com letras e números.")


def create_session_token(user_id: str, token_version: int) -> str:
    payload = {
        "sub": user_id,
        "tv": token_version,
        "exp": datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_session_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        return None


def new_reset_token() -> tuple[str, str]:
    """Returns (raw token for the e-mail link, sha256 digest stored in the DB)."""
    raw = secrets.token_urlsafe(32)
    return raw, hashlib.sha256(raw.encode()).hexdigest()


def digest_token(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


_hits: dict[str, deque] = defaultdict(deque)


def rate_limit(key: str, limit: int, window_seconds: int) -> None:
    """In-memory sliding window — technical protection against automated abuse."""
    now = time.monotonic()
    dq = _hits[key]
    while dq and now - dq[0] > window_seconds:
        dq.popleft()
    if len(dq) >= limit:
        raise HTTPException(429, "Muitas tentativas em pouco tempo. Aguarde alguns instantes e tente novamente.")
    dq.append(now)


def aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)

# Reusable server-side secret encryption for payment provider credentials.
def _secret_fernet():
    import base64
    from cryptography.fernet import Fernet
    raw = hashlib.sha256(JWT_SECRET.encode()).digest()
    return Fernet(base64.urlsafe_b64encode(raw))


def encrypt_secret(value: str) -> str:
    return _secret_fernet().encrypt(value.encode()).decode()


def decrypt_secret(value: str) -> str:
    from cryptography.fernet import InvalidToken
    try:
        return _secret_fernet().decrypt(value.encode()).decode()
    except (InvalidToken, ValueError) as exc:
        raise HTTPException(500, "A configuração secreta não pôde ser lida.") from exc

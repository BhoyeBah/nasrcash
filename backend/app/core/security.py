import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import UnauthorizedError

settings = get_settings()

pin_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"
    ADMIN_ACCESS = "admin_access"


@dataclass(frozen=True)
class IssuedToken:
    token: str
    jti: str
    expires_at: datetime


def hash_secret(secret: str) -> str:
    """Bcrypt-hash a short secret (PIN or OTP code). Never store either in clear."""
    return pin_context.hash(secret)


def verify_secret(secret: str, secret_hash: str) -> bool:
    return pin_context.verify(secret, secret_hash)


# Aliases kept for call-site clarity.
hash_pin = hash_secret
verify_pin = verify_secret


def _create_token(subject: str, token_type: TokenType, expires_delta: timedelta) -> IssuedToken:
    now = datetime.now(timezone.utc)
    expires_at = now + expires_delta
    jti = str(uuid.uuid4())
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type.value,
        "iat": now,
        "exp": expires_at,
        "jti": jti,
    }
    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return IssuedToken(token=token, jti=jti, expires_at=expires_at)


def create_access_token(user_id: uuid.UUID | str) -> IssuedToken:
    return _create_token(
        str(user_id),
        TokenType.ACCESS,
        timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )


def create_admin_access_token(admin_id: uuid.UUID | str) -> IssuedToken:
    # Deliberately separate token type from the mobile user's ACCESS token —
    # a leaked user token must never authenticate against admin endpoints.
    return _create_token(
        str(admin_id),
        TokenType.ADMIN_ACCESS,
        timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )


def create_refresh_token(user_id: uuid.UUID | str) -> IssuedToken:
    return _create_token(
        str(user_id),
        TokenType.REFRESH,
        timedelta(days=settings.jwt_refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise UnauthorizedError("Invalid or expired token") from exc

    if payload.get("type") != expected_type.value:
        raise UnauthorizedError(f"Expected a {expected_type.value} token")

    return payload

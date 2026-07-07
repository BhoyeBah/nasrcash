import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.core.security import TokenType, decode_token
from app.modules.auth.models import User, UserStatus

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if credentials is None:
        raise UnauthorizedError("Authentification requise")

    payload = decode_token(credentials.credentials, TokenType.ACCESS)
    user = await db.get(User, uuid.UUID(payload["sub"]))
    if user is None or user.status == UserStatus.CLOSED.value:
        raise UnauthorizedError("Utilisateur introuvable ou compte fermé")

    return user

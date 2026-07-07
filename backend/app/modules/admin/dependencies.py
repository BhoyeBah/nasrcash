import uuid

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import UnauthorizedError
from app.core.permissions import AdminRole, require_role
from app.core.security import TokenType, decode_token
from app.modules.admin.models import AdminUser

admin_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(admin_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> AdminUser:
    if credentials is None:
        raise UnauthorizedError("Authentification admin requise")

    payload = decode_token(credentials.credentials, TokenType.ADMIN_ACCESS)
    admin = await db.get(AdminUser, uuid.UUID(payload["sub"]))
    if admin is None or not admin.is_active:
        raise UnauthorizedError("Compte admin introuvable ou désactivé")

    return admin


def require_admin_roles(allowed: set[AdminRole]):
    async def _check(admin: AdminUser = Depends(get_current_admin)) -> AdminUser:
        require_role(AdminRole(admin.role), allowed)
        return admin

    return _check

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.permissions import AdminRole
from app.core.security import hash_secret
from app.modules.admin.models import AdminUser

settings = get_settings()


async def seed_bootstrap_admin(db: AsyncSession) -> None:
    result = await db.execute(
        select(AdminUser).where(AdminUser.email == settings.admin_bootstrap_email)
    )
    if result.scalar_one_or_none() is not None:
        return

    db.add(
        AdminUser(
            email=settings.admin_bootstrap_email,
            password_hash=hash_secret(settings.admin_bootstrap_password),
            role=AdminRole.SUPER_ADMIN.value,
        )
    )
    await db.flush()

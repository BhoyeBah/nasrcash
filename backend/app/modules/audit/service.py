import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.audit.models import AuditLog


class AuditService:
    """Write-only interface to the audit journal. There is deliberately no
    update or delete method — this table is append-only by construction."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log(
        self,
        actor_type: str,
        action: str,
        actor_id: uuid.UUID | None = None,
        target_type: str | None = None,
        target_id: str | None = None,
        context: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditLog:
        entry = AuditLog(
            actor_type=actor_type,
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            context=context or {},
            ip_address=ip_address,
        )
        self.db.add(entry)
        await self.db.flush()
        return entry

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ForbiddenError, NotFoundError
from app.modules.notifications.models import Notification


class NotificationService:
    """In-app notifications only for now — push (FCM/OneSignal) and SMS are
    separate channels to be wired up once a real provider is chosen."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self, user_id: uuid.UUID, notification_type: str, title: str, body: str,
        context: dict | None = None,
    ) -> Notification:
        notification = Notification(
            user_id=user_id, type=notification_type, title=title, body=body,
            context=context or {},
        )
        self.db.add(notification)
        await self.db.flush()
        return notification

    async def list_for_user(
        self, user_id: uuid.UUID, unread_only: bool = False, limit: int = 50, offset: int = 0
    ) -> list[Notification]:
        query = select(Notification).where(Notification.user_id == user_id)
        if unread_only:
            query = query.where(Notification.read_at.is_(None))
        query = query.order_by(Notification.created_at.desc()).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return list(result.scalars())

    async def unread_count(self, user_id: uuid.UUID) -> int:
        result = await self.db.execute(
            select(func.count())
            .select_from(Notification)
            .where(Notification.user_id == user_id, Notification.read_at.is_(None))
        )
        return result.scalar_one()

    async def mark_read(self, notification_id: uuid.UUID, user_id: uuid.UUID) -> Notification:
        notification = await self.db.get(Notification, notification_id)
        if notification is None:
            raise NotFoundError("Notification introuvable")
        if notification.user_id != user_id:
            raise ForbiddenError("Cette notification n'appartient pas à cet utilisateur")
        if notification.read_at is None:
            notification.read_at = datetime.now(timezone.utc)
            await self.db.flush()
        return notification

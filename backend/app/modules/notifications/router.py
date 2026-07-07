import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.notifications.schemas import NotificationResponse
from app.modules.notifications.service import NotificationService

router = APIRouter(prefix="/api/v1/notifications", tags=["notifications"])


@router.get("", response_model=list[NotificationResponse])
async def list_notifications(
    unread_only: bool = Query(False),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    return await service.list_for_user(
        current_user.id, unread_only=unread_only, limit=limit, offset=offset
    )


@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = NotificationService(db)
    count = await service.unread_count(current_user.id)
    return {"unread_count": count}


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    notification_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = NotificationService(db)
    notification = await service.mark_read(notification_id, current_user.id)
    await db.commit()
    return notification

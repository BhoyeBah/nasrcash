import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.support.schemas import (
    MessageCreateRequest,
    MessageResponse,
    TicketCreateRequest,
    TicketDetailResponse,
    TicketResponse,
)
from app.modules.support.service import SupportService

router = APIRouter(prefix="/api/v1/support", tags=["support"])


@router.post("/tickets", response_model=TicketResponse)
async def create_ticket(
    payload: TicketCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SupportService(db)
    ticket = await service.create_ticket(
        current_user.id, payload.subject, payload.category, payload.message
    )
    await db.commit()
    return ticket


@router.get("/tickets", response_model=list[TicketResponse])
async def list_my_tickets(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SupportService(db)
    return await service.list_for_user(current_user.id)


@router.get("/tickets/{ticket_id}", response_model=TicketDetailResponse)
async def get_ticket(
    ticket_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SupportService(db)
    ticket = await service.get_ticket(ticket_id, current_user.id)
    messages = await service.list_messages(ticket_id)
    return TicketDetailResponse(ticket=ticket, messages=messages)


@router.post("/tickets/{ticket_id}/messages", response_model=MessageResponse)
async def add_message(
    ticket_id: uuid.UUID,
    payload: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = SupportService(db)
    ticket = await service.get_ticket(ticket_id, current_user.id)
    message = await service.add_user_message(ticket, current_user.id, payload.body)
    await db.commit()
    return message

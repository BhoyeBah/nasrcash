import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, ForbiddenError, NotFoundError, ValidationError
from app.modules.notifications.models import NotificationType
from app.modules.notifications.service import NotificationService
from app.modules.support.models import (
    OPEN_TICKET_STATUSES,
    SupportMessage,
    SupportTicket,
    TicketCategory,
    TicketStatus,
)

CLOSED_TICKET_STATUSES = (TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value)


class SupportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.notifications = NotificationService(db)

    async def create_ticket(
        self, user_id: uuid.UUID, subject: str, category: str, message: str
    ) -> SupportTicket:
        if category not in {c.value for c in TicketCategory}:
            raise ValidationError(f"Catégorie de ticket invalide : {category}")

        ticket = SupportTicket(user_id=user_id, subject=subject, category=category)
        self.db.add(ticket)
        await self.db.flush()

        self.db.add(
            SupportMessage(
                ticket_id=ticket.id, sender_type="user", sender_id=user_id, body=message
            )
        )
        await self.db.flush()
        return ticket

    async def get_ticket(
        self, ticket_id: uuid.UUID, user_id: uuid.UUID | None = None
    ) -> SupportTicket:
        ticket = await self.db.get(SupportTicket, ticket_id)
        if ticket is None:
            raise NotFoundError("Ticket introuvable")
        if user_id is not None and ticket.user_id != user_id:
            raise ForbiddenError("Ce ticket n'appartient pas à cet utilisateur")
        return ticket

    async def list_messages(self, ticket_id: uuid.UUID) -> list[SupportMessage]:
        result = await self.db.execute(
            select(SupportMessage)
            .where(SupportMessage.ticket_id == ticket_id)
            .order_by(SupportMessage.created_at.asc())
        )
        return list(result.scalars())

    async def list_for_user(self, user_id: uuid.UUID) -> list[SupportTicket]:
        result = await self.db.execute(
            select(SupportTicket)
            .where(SupportTicket.user_id == user_id)
            .order_by(SupportTicket.created_at.desc())
        )
        return list(result.scalars())

    async def add_user_message(self, ticket: SupportTicket, user_id: uuid.UUID, body: str) -> SupportMessage:
        if ticket.status in CLOSED_TICKET_STATUSES:
            raise ConflictError(f"Ce ticket est '{ticket.status}' — impossible d'y répondre")
        message = SupportMessage(
            ticket_id=ticket.id, sender_type="user", sender_id=user_id, body=body
        )
        self.db.add(message)
        # A customer reply on a ticket a support agent was already handling
        # should resurface it — but doesn't retroactively reopen a resolved one.
        if ticket.status == TicketStatus.IN_PROGRESS.value:
            ticket.status = TicketStatus.OPEN.value
        await self.db.flush()
        return message

    # --- admin management ---

    async def list_all(self, status: str | None = None) -> list[SupportTicket]:
        query = select(SupportTicket).order_by(SupportTicket.created_at.desc())
        if status is not None:
            query = query.where(SupportTicket.status == status)
        result = await self.db.execute(query)
        return list(result.scalars())

    async def add_admin_reply(
        self, ticket: SupportTicket, admin_id: uuid.UUID, body: str
    ) -> SupportMessage:
        if ticket.status in CLOSED_TICKET_STATUSES:
            raise ConflictError(f"Ce ticket est '{ticket.status}' — impossible d'y répondre")
        message = SupportMessage(
            ticket_id=ticket.id, sender_type="admin", sender_id=admin_id, body=body
        )
        self.db.add(message)
        ticket.status = TicketStatus.IN_PROGRESS.value
        await self.db.flush()
        await self.notifications.create(
            ticket.user_id, NotificationType.SUPPORT_REPLY.value,
            "Réponse du support",
            f"Le support a répondu à votre ticket « {ticket.subject} ».",
        )
        return message

    async def close_ticket(self, ticket: SupportTicket) -> SupportTicket:
        if ticket.status == TicketStatus.CLOSED.value:
            raise ConflictError("Ce ticket est déjà fermé")
        ticket.status = TicketStatus.CLOSED.value
        await self.db.flush()
        return ticket

    async def resolve_ticket(self, ticket: SupportTicket) -> SupportTicket:
        if ticket.status not in OPEN_TICKET_STATUSES:
            raise ConflictError(f"Impossible de résoudre un ticket '{ticket.status}'")
        ticket.status = TicketStatus.RESOLVED.value
        await self.db.flush()
        return ticket

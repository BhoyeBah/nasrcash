import uuid
from enum import StrEnum

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, TimestampMixin, UUIDPrimaryKeyMixin


class TicketCategory(StrEnum):
    GENERAL = "general"
    KYC = "kyc"
    TOPUP = "topup"
    WITHDRAWAL = "withdrawal"
    CARD = "card"
    PAYMENT = "payment"


class TicketStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


OPEN_TICKET_STATUSES = (TicketStatus.OPEN.value, TicketStatus.IN_PROGRESS.value)


class SupportTicket(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A customer support ticket — the in-app channel from cahier des
    charges §14 (WhatsApp is the other channel, out of scope: it needs a
    WhatsApp Business API key we don't have in this sandbox)."""

    __tablename__ = "support_tickets"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(
        String(20), default=TicketCategory.GENERAL.value, nullable=False
    )
    status: Mapped[str] = mapped_column(
        String(20), default=TicketStatus.OPEN.value, nullable=False, index=True
    )


class SupportMessage(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """One message in a ticket thread — either from the customer or from a
    support admin. Append-only, like the rest of the thread history."""

    __tablename__ = "support_messages"

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("support_tickets.id"), nullable=False, index=True
    )
    sender_type: Mapped[str] = mapped_column(String(10), nullable=False)  # user | admin
    sender_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

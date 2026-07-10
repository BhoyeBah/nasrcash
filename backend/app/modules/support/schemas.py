import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TicketCreateRequest(BaseModel):
    subject: str = Field(min_length=1, max_length=200)
    category: str = "general"
    message: str = Field(min_length=1, max_length=4000)


class MessageCreateRequest(BaseModel):
    body: str = Field(min_length=1, max_length=4000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ticket_id: uuid.UUID
    sender_type: str
    sender_id: uuid.UUID
    body: str
    created_at: datetime


class TicketResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    subject: str
    category: str
    status: str
    created_at: datetime


class TicketDetailResponse(BaseModel):
    ticket: TicketResponse
    messages: list[MessageResponse]

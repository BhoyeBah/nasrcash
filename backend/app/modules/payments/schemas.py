import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class SimulatePaymentRequest(BaseModel):
    merchant_name: str = Field(min_length=1, max_length=150)
    merchant_amount: Decimal = Field(gt=0)
    merchant_currency: str = Field(min_length=3, max_length=3)
    provider_reference: str | None = None


class SimulateDeclineRequest(BaseModel):
    merchant_name: str = Field(min_length=1, max_length=150)
    merchant_amount: Decimal = Field(gt=0)
    merchant_currency: str = Field(min_length=3, max_length=3)
    provider_reference: str | None = None
    reason: str = "card_blocked"


class CardPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    card_id: uuid.UUID
    merchant_name: str
    merchant_currency: str
    merchant_amount: Decimal
    fx_rate: Decimal
    local_currency: str
    local_amount: Decimal
    fees_amount: Decimal
    total_debited: Decimal
    status: str
    decline_reason: str | None
    provider_reference: str
    created_at: datetime

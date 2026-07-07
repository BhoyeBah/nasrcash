import uuid
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CardResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    masked_pan: str
    last4: str
    brand: str
    displayed_currency: str
    status: str
    nickname: str | None
    expiry_month: int
    expiry_year: int


class CardBalanceResponse(BaseModel):
    card_id: uuid.UUID
    currency_code: str
    available_balance: Decimal


class CardFundRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    idempotency_key: str = Field(min_length=1, max_length=100)

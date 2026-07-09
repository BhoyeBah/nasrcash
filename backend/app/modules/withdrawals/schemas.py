import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class WithdrawalRequest(BaseModel):
    amount: Decimal = Field(gt=0)
    provider_name: str


class WithdrawalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    wallet_id: uuid.UUID
    amount: Decimal
    fee_amount: Decimal
    net_amount: Decimal
    currency_code: str
    provider_name: str
    status: str
    failure_reason: str | None
    confirmed_at: datetime | None
    created_at: datetime

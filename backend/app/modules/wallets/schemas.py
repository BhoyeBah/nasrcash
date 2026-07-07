import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class WalletResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    country_code: str
    currency_code: str
    status: str


class WalletBalanceResponse(BaseModel):
    wallet_id: uuid.UUID
    currency_code: str
    available_balance: Decimal


class LedgerEntryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    direction: str
    amount: Decimal
    currency: str
    description: str | None
    created_at: datetime

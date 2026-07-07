import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AdminLoginRequest(BaseModel):
    email: str
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DashboardResponse(BaseModel):
    users_count: int
    kyc_pending_count: int
    cards_count: int
    successful_topups_volume: Decimal
    settled_payments_volume: Decimal
    declined_payments_count: int
    revenue_total: Decimal
    total_wallet_cached_balance: Decimal


class AdminUserListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    phone: str
    country_code: str
    status: str
    kyc_level: int
    created_at: datetime


class AdminKycRejectRequest(BaseModel):
    reason: str


class AdminKycPendingItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    level_requested: int
    status: str
    submitted_at: datetime | None


class AdminTransactionItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    account_id: str
    direction: str
    amount: Decimal
    currency: str
    created_at: datetime

import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class FeeRuleCreateRequest(BaseModel):
    fee_type: str
    country_code: str | None = None
    provider_name: str | None = None
    kyc_level: int | None = None
    rate: Decimal | None = None
    fixed_amount: Decimal | None = None


class FeeRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    fee_type: str
    country_code: str | None
    provider_name: str | None
    kyc_level: int | None
    rate: Decimal | None
    fixed_amount: Decimal
    is_active: bool
    created_at: datetime

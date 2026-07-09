import uuid
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class LimitRuleCreateRequest(BaseModel):
    limit_type: str
    country_code: str | None = None
    kyc_level: int | None = None
    max_amount: Decimal | None = None
    max_count: int | None = None


class LimitRuleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    limit_type: str
    country_code: str | None
    kyc_level: int | None
    max_amount: Decimal | None
    max_count: int | None
    is_active: bool
    created_at: datetime

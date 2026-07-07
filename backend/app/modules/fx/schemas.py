from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class UpdateFxRateRequest(BaseModel):
    base_currency: str = Field(min_length=3, max_length=3)
    quote_currency: str = Field(min_length=3, max_length=3)
    rate: Decimal = Field(gt=0)


class FxRateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    base_currency: str
    quote_currency: str
    rate: Decimal
    created_at: datetime

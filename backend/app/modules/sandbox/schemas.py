import uuid

from pydantic import BaseModel


class SimulateFailureRequest(BaseModel):
    reason: str = "insufficient_funds"


class SimulateRefundRequest(BaseModel):
    payment_id: uuid.UUID

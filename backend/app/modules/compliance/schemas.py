import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ComplianceAlertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    alert_type: str
    severity: str
    status: str
    context: dict
    resolved_at: datetime | None
    resolved_by: uuid.UUID | None
    resolution_notes: str | None
    created_at: datetime


class ComplianceAlertResolveRequest(BaseModel):
    resolution_notes: str | None = None

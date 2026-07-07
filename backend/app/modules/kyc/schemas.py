import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class KycProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    level_requested: int
    status: str
    rejection_reason: str | None
    submitted_at: datetime | None
    reviewed_at: datetime | None


class KycDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    document_type: str
    original_filename: str


class KycStatusResponse(BaseModel):
    profile: KycProfileResponse | None
    documents: list[KycDocumentResponse]
    current_kyc_level: int

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.kyc.schemas import KycDocumentResponse, KycProfileResponse, KycStatusResponse
from app.modules.kyc.service import KycService

router = APIRouter(prefix="/api/v1/kyc", tags=["kyc"])


@router.post("/start", response_model=KycProfileResponse)
async def start(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = KycService(db)
    profile = await service.start(current_user)
    await db.commit()
    return profile


@router.post("/documents", response_model=KycDocumentResponse)
async def upload_document(
    document_type: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = KycService(db)
    document = await service.add_document(current_user, document_type, file)
    await db.commit()
    return document


@router.post("/submit", response_model=KycProfileResponse)
async def submit(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = KycService(db)
    profile = await service.submit(current_user)
    await db.commit()
    return profile


@router.get("/status", response_model=KycStatusResponse)
async def get_status(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    service = KycService(db)
    profile, documents = await service.get_status(current_user)
    return KycStatusResponse(
        profile=profile, documents=documents, current_kyc_level=current_user.kyc_level
    )

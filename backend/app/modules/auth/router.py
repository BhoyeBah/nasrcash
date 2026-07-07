from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.modules.auth.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.schemas import (
    ChangePinRequest,
    ForgotPinRequest,
    ForgotPinResponse,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    RegisterResponse,
    ResetPinRequest,
    TokenPairResponse,
    VerifyOtpRequest,
)
from app.modules.auth.service import AuthService

settings = get_settings()
router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    user, otp_code = await service.register(payload.phone, payload.country_code, payload.pin)
    await db.commit()
    return RegisterResponse(
        user_id=user.id,
        phone=user.phone,
        otp_expires_in_seconds=settings.otp_expire_seconds,
        sandbox_otp_code=otp_code if settings.sandbox_mode else None,
    )


@router.post("/verify-otp", response_model=TokenPairResponse)
async def verify_otp(payload: VerifyOtpRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    access, refresh = await service.verify_otp(
        payload.phone, payload.code, payload.device_id, payload.device_name
    )
    await db.commit()
    return TokenPairResponse(access_token=access.token, refresh_token=refresh.token)


@router.post("/login", response_model=TokenPairResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    access, refresh = await service.login(
        payload.phone, payload.pin, payload.device_id, payload.device_name
    )
    await db.commit()
    return TokenPairResponse(access_token=access.token, refresh_token=refresh.token)


@router.post("/refresh", response_model=TokenPairResponse)
async def refresh(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    access, refresh_token = await service.refresh(payload.refresh_token)
    await db.commit()
    return TokenPairResponse(access_token=access.token, refresh_token=refresh_token.token)


@router.post("/logout", response_model=MessageResponse)
async def logout(payload: LogoutRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.logout(payload.refresh_token, payload.all_devices)
    await db.commit()
    return MessageResponse(message="Déconnexion réussie")


@router.post("/change-pin", response_model=MessageResponse)
async def change_pin(
    payload: ChangePinRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = AuthService(db)
    await service.change_pin(current_user, payload.current_pin, payload.new_pin)
    await db.commit()
    return MessageResponse(message="PIN modifié avec succès")


@router.post("/forgot-pin", response_model=ForgotPinResponse)
async def forgot_pin(payload: ForgotPinRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    otp_code = await service.forgot_pin(payload.phone)
    await db.commit()
    return ForgotPinResponse(
        message="Si ce numéro est enregistré, un code a été envoyé",
        otp_expires_in_seconds=settings.otp_expire_seconds,
        sandbox_otp_code=otp_code if settings.sandbox_mode else None,
    )


@router.post("/reset-pin", response_model=MessageResponse)
async def reset_pin(payload: ResetPinRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    await service.reset_pin(payload.phone, payload.code, payload.new_pin)
    await db.commit()
    return MessageResponse(message="PIN réinitialisé avec succès")

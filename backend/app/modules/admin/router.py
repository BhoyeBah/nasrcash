from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import AdminRole
from app.core.security import create_admin_access_token
from app.modules.admin.dependencies import require_admin_roles
from app.modules.admin.schemas import (
    AdminKycPendingItem,
    AdminLoginRequest,
    AdminTokenResponse,
    AdminTransactionItem,
    AdminUserListItem,
    DashboardResponse,
)
from app.modules.admin.service import AdminService

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

# Reading dashboard/user/transaction data is safe for every internal role;
# only mutating actions (approve KYC, block a card, adjust a balance) need
# tighter scoping — those arrive with the write endpoints in a later bloc.
ANY_ADMIN_ROLE = set(AdminRole)
KYC_VISIBILITY_ROLES = {
    AdminRole.SUPER_ADMIN,
    AdminRole.COMPLIANCE_OFFICER,
    AdminRole.RISK_ANALYST,
    AdminRole.AUDITOR,
}


@router.post("/auth/login", response_model=AdminTokenResponse)
async def admin_login(payload: AdminLoginRequest, db: AsyncSession = Depends(get_db)):
    service = AdminService(db)
    admin = await service.authenticate(payload.email, payload.password)
    token = create_admin_access_token(admin.id)
    return AdminTokenResponse(access_token=token.token)


@router.get("/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ANY_ADMIN_ROLE)),
):
    service = AdminService(db)
    return await service.get_dashboard()


@router.get("/users", response_model=list[AdminUserListItem])
async def list_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ANY_ADMIN_ROLE)),
):
    service = AdminService(db)
    return await service.list_users(limit=limit, offset=offset)


@router.get("/kyc/pending", response_model=list[AdminKycPendingItem])
async def list_kyc_pending(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(KYC_VISIBILITY_ROLES)),
):
    service = AdminService(db)
    return await service.list_kyc_pending(limit=limit, offset=offset)


@router.get("/transactions", response_model=list[AdminTransactionItem])
async def list_transactions(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ANY_ADMIN_ROLE)),
):
    service = AdminService(db)
    return await service.list_transactions(limit=limit, offset=offset)

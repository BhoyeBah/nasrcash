import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.permissions import FEES_LIMITS_WRITE_ROLES, KYC_REVIEWER_ROLES, AdminRole
from app.core.rate_limit import rate_limiter
from app.core.security import create_admin_access_token
from app.modules.admin.dependencies import require_admin_roles
from app.modules.admin.models import AdminUser
from app.modules.admin.schemas import (
    AdminKycPendingItem,
    AdminKycRejectRequest,
    AdminLoginRequest,
    AdminTokenResponse,
    AdminTransactionItem,
    AdminUserListItem,
    DashboardResponse,
)
from app.modules.admin.service import AdminService
from app.modules.kyc.schemas import KycProfileResponse
from app.modules.kyc.service import KycService
from app.modules.limits.schemas import LimitRuleCreateRequest, LimitRuleResponse
from app.modules.limits.service import LimitService

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

# Reading dashboard/user/transaction data is safe for every internal role;
# only mutating actions (approve/reject KYC, block a card, adjust a balance)
# need tighter scoping.
ANY_ADMIN_ROLE = set(AdminRole)
KYC_VISIBILITY_ROLES = {
    AdminRole.SUPER_ADMIN,
    AdminRole.COMPLIANCE_OFFICER,
    AdminRole.RISK_ANALYST,
    AdminRole.AUDITOR,
}


@router.post(
    "/auth/login",
    response_model=AdminTokenResponse,
    dependencies=[Depends(rate_limiter("admin-login", max_requests=10, window_seconds=300))],
)
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


@router.post("/kyc/{profile_id}/approve", response_model=KycProfileResponse)
async def approve_kyc(
    profile_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_admin_roles(KYC_REVIEWER_ROLES)),
):
    service = KycService(db)
    profile = await service.approve(profile_id, reviewer_id=str(admin.id))
    await db.commit()
    return profile


@router.post("/kyc/{profile_id}/reject", response_model=KycProfileResponse)
async def reject_kyc(
    profile_id: uuid.UUID,
    payload: AdminKycRejectRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_admin_roles(KYC_REVIEWER_ROLES)),
):
    service = KycService(db)
    profile = await service.reject(profile_id, reviewer_id=str(admin.id), reason=payload.reason)
    await db.commit()
    return profile


@router.get("/limits", response_model=list[LimitRuleResponse])
async def list_limit_rules(
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ANY_ADMIN_ROLE)),
):
    service = LimitService(db)
    return await service.list_rules(active_only=active_only)


@router.post("/limits", response_model=LimitRuleResponse)
async def create_limit_rule(
    payload: LimitRuleCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(FEES_LIMITS_WRITE_ROLES)),
):
    service = LimitService(db)
    rule = await service.create_rule(
        payload.limit_type, payload.country_code, payload.kyc_level,
        payload.max_amount, payload.max_count,
    )
    await db.commit()
    return rule


@router.post("/limits/{rule_id}/deactivate", response_model=LimitRuleResponse)
async def deactivate_limit_rule(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(FEES_LIMITS_WRITE_ROLES)),
):
    service = LimitService(db)
    rule = await service.deactivate_rule(rule_id)
    await db.commit()
    return rule

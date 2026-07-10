import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.permissions import (
    ACCOUNTING_EXPORT_ROLES,
    ADMIN_MANAGEMENT_ROLES,
    AUDIT_VIEW_ROLES,
    CARDS_WRITE_ROLES,
    COMPLIANCE_RESOLVE_ROLES,
    COMPLIANCE_VIEW_ROLES,
    FEES_LIMITS_WRITE_ROLES,
    KYC_REVIEWER_ROLES,
    SUPPORT_ROLES,
    AdminRole,
)
from app.core.rate_limit import rate_limiter
from app.core.security import create_admin_access_token
from app.modules.admin.dependencies import require_admin_roles
from app.modules.admin.models import AdminUser
from app.modules.admin.schemas import (
    AdminAccountActiveUpdateRequest,
    AdminAccountCreateRequest,
    AdminAccountResponse,
    AdminAccountRoleUpdateRequest,
    AdminCardListItem,
    AdminKycPendingItem,
    AdminKycRejectRequest,
    AdminLoginRequest,
    AdminTokenResponse,
    AdminTransactionItem,
    AdminUserListItem,
    DashboardResponse,
)
from app.modules.admin.service import AdminService
from app.modules.audit.schemas import AuditLogResponse
from app.modules.audit.service import AuditService
from app.modules.cards.models import Card
from app.modules.cards.schemas import CardResponse
from app.modules.cards.service import CardService
from app.modules.compliance.schemas import (
    ComplianceAlertResolveRequest,
    ComplianceAlertResponse,
    RiskScoreResponse,
)
from app.modules.compliance.service import ComplianceService
from app.modules.fees.schemas import FeeRuleCreateRequest, FeeRuleResponse
from app.modules.fees.service import FeeService
from app.modules.fx.schemas import FxRateResponse, UpdateFxRateRequest
from app.modules.fx.service import FXService
from app.modules.kyc.schemas import KycProfileResponse
from app.modules.kyc.service import KycService
from app.modules.limits.schemas import LimitRuleCreateRequest, LimitRuleResponse
from app.modules.limits.service import LimitService
from app.modules.support.schemas import (
    MessageCreateRequest,
    MessageResponse,
    TicketDetailResponse,
    TicketResponse,
)
from app.modules.support.service import SupportService

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


@router.get("/fees", response_model=list[FeeRuleResponse])
async def list_fee_rules(
    active_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ANY_ADMIN_ROLE)),
):
    service = FeeService(db)
    return await service.list_rules(active_only=active_only)


@router.post("/fees", response_model=FeeRuleResponse)
async def create_fee_rule(
    payload: FeeRuleCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(FEES_LIMITS_WRITE_ROLES)),
):
    service = FeeService(db)
    rule = await service.create_rule(
        payload.fee_type, payload.country_code, payload.provider_name, payload.kyc_level,
        payload.rate, payload.fixed_amount,
    )
    await db.commit()
    return rule


@router.post("/fees/{rule_id}/deactivate", response_model=FeeRuleResponse)
async def deactivate_fee_rule(
    rule_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(FEES_LIMITS_WRITE_ROLES)),
):
    service = FeeService(db)
    rule = await service.deactivate_rule(rule_id)
    await db.commit()
    return rule


@router.get("/compliance/alerts", response_model=list[ComplianceAlertResponse])
async def list_compliance_alerts(
    status: str | None = Query(None),
    severity: str | None = Query(None),
    user_id: uuid.UUID | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(COMPLIANCE_VIEW_ROLES)),
):
    service = ComplianceService(db)
    return await service.list_alerts(status=status, severity=severity, user_id=user_id)


@router.post("/compliance/alerts/{alert_id}/resolve", response_model=ComplianceAlertResponse)
async def resolve_compliance_alert(
    alert_id: uuid.UUID,
    payload: ComplianceAlertResolveRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_admin_roles(COMPLIANCE_RESOLVE_ROLES)),
):
    service = ComplianceService(db)
    alert = await service.resolve_alert(alert_id, admin.id, payload.resolution_notes)
    await db.commit()
    return alert


@router.post("/compliance/alerts/{alert_id}/dismiss", response_model=ComplianceAlertResponse)
async def dismiss_compliance_alert(
    alert_id: uuid.UUID,
    payload: ComplianceAlertResolveRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_admin_roles(COMPLIANCE_RESOLVE_ROLES)),
):
    service = ComplianceService(db)
    alert = await service.dismiss_alert(alert_id, admin.id, payload.resolution_notes)
    await db.commit()
    return alert


@router.get("/compliance/users/{user_id}/risk-score", response_model=RiskScoreResponse)
async def get_user_risk_score(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(COMPLIANCE_VIEW_ROLES)),
):
    service = ComplianceService(db)
    return await service.compute_risk_score(user_id)


@router.post("/compliance/users/{user_id}/unfreeze", response_model=AdminUserListItem)
async def unfreeze_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_admin_roles(COMPLIANCE_RESOLVE_ROLES)),
):
    service = ComplianceService(db)
    user = await service.unfreeze_user(user_id, admin.id)
    await db.commit()
    return user


@router.get("/compliance/report")
async def export_compliance_report(
    since: datetime | None = Query(None),
    until: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(COMPLIANCE_VIEW_ROLES)),
):
    service = ComplianceService(db)
    csv_content = await service.export_alerts_csv(since=since, until=until)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=compliance_report.csv"},
    )


@router.get("/cards", response_model=list[AdminCardListItem])
async def list_cards(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ANY_ADMIN_ROLE)),
):
    service = AdminService(db)
    return await service.list_cards(limit=limit, offset=offset)


@router.post("/cards/{card_id}/block", response_model=CardResponse)
async def block_card(
    card_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_admin_roles(CARDS_WRITE_ROLES)),
):
    card = await db.get(Card, card_id)
    if card is None:
        raise NotFoundError("Carte introuvable")
    service = CardService(db)
    card = await service.admin_block(card, admin.id)
    await db.commit()
    return card


@router.post("/cards/{card_id}/unblock", response_model=CardResponse)
async def unblock_card(
    card_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_admin_roles(CARDS_WRITE_ROLES)),
):
    card = await db.get(Card, card_id)
    if card is None:
        raise NotFoundError("Carte introuvable")
    service = CardService(db)
    card = await service.admin_unblock(card, admin.id)
    await db.commit()
    return card


@router.get("/fx-rates", response_model=list[FxRateResponse])
async def list_fx_rates(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ANY_ADMIN_ROLE)),
):
    service = FXService(db)
    return await service.list_rates()


@router.post("/fx-rates", response_model=FxRateResponse)
async def create_fx_rate(
    payload: UpdateFxRateRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(FEES_LIMITS_WRITE_ROLES)),
):
    service = FXService(db)
    fx_rate = await service.set_rate(payload.base_currency, payload.quote_currency, payload.rate)
    await db.commit()
    return fx_rate


@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def list_audit_logs(
    actor_type: str | None = Query(None),
    action: str | None = Query(None),
    target_type: str | None = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(AUDIT_VIEW_ROLES)),
):
    service = AuditService(db)
    return await service.list_logs(
        actor_type=actor_type, action=action, target_type=target_type, limit=limit, offset=offset
    )


@router.get("/accounting/export")
async def export_accounting_ledger(
    since: datetime | None = Query(None),
    until: datetime | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ACCOUNTING_EXPORT_ROLES)),
):
    service = AdminService(db)
    csv_content = await service.export_ledger_csv(since=since, until=until)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ledger_export.csv"},
    )


@router.get("/accounts", response_model=list[AdminAccountResponse])
async def list_admin_accounts(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ADMIN_MANAGEMENT_ROLES)),
):
    service = AdminService(db)
    return await service.list_admin_users()


@router.post("/accounts", response_model=AdminAccountResponse)
async def create_admin_account(
    payload: AdminAccountCreateRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ADMIN_MANAGEMENT_ROLES)),
):
    service = AdminService(db)
    account = await service.create_admin_user(payload.email, payload.password, payload.role)
    await db.commit()
    return account


@router.post("/accounts/{admin_id}/role", response_model=AdminAccountResponse)
async def update_admin_account_role(
    admin_id: uuid.UUID,
    payload: AdminAccountRoleUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ADMIN_MANAGEMENT_ROLES)),
):
    service = AdminService(db)
    account = await service.update_admin_role(admin_id, payload.role)
    await db.commit()
    return account


@router.post("/accounts/{admin_id}/active", response_model=AdminAccountResponse)
async def update_admin_account_active(
    admin_id: uuid.UUID,
    payload: AdminAccountActiveUpdateRequest,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(ADMIN_MANAGEMENT_ROLES)),
):
    service = AdminService(db)
    account = await service.set_admin_active(admin_id, payload.is_active)
    await db.commit()
    return account


@router.get("/support/tickets", response_model=list[TicketResponse])
async def list_support_tickets(
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(SUPPORT_ROLES)),
):
    service = SupportService(db)
    return await service.list_all(status=status)


@router.get("/support/tickets/{ticket_id}", response_model=TicketDetailResponse)
async def get_support_ticket(
    ticket_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(SUPPORT_ROLES)),
):
    service = SupportService(db)
    ticket = await service.get_ticket(ticket_id)
    messages = await service.list_messages(ticket_id)
    return TicketDetailResponse(ticket=ticket, messages=messages)


@router.post("/support/tickets/{ticket_id}/messages", response_model=MessageResponse)
async def reply_support_ticket(
    ticket_id: uuid.UUID,
    payload: MessageCreateRequest,
    db: AsyncSession = Depends(get_db),
    admin: AdminUser = Depends(require_admin_roles(SUPPORT_ROLES)),
):
    service = SupportService(db)
    ticket = await service.get_ticket(ticket_id)
    message = await service.add_admin_reply(ticket, admin.id, payload.body)
    await db.commit()
    return message


@router.post("/support/tickets/{ticket_id}/resolve", response_model=TicketResponse)
async def resolve_support_ticket(
    ticket_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(SUPPORT_ROLES)),
):
    service = SupportService(db)
    ticket = await service.get_ticket(ticket_id)
    ticket = await service.resolve_ticket(ticket)
    await db.commit()
    return ticket


@router.post("/support/tickets/{ticket_id}/close", response_model=TicketResponse)
async def close_support_ticket(
    ticket_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(require_admin_roles(SUPPORT_ROLES)),
):
    service = SupportService(db)
    ticket = await service.get_ticket(ticket_id)
    ticket = await service.close_ticket(ticket)
    await db.commit()
    return ticket

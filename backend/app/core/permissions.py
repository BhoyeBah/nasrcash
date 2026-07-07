from enum import StrEnum

from app.core.exceptions import ForbiddenError


class AdminRole(StrEnum):
    SUPER_ADMIN = "super_admin"
    COUNTRY_ADMIN = "country_admin"
    COMPLIANCE_OFFICER = "compliance_officer"
    FINANCE_MANAGER = "finance_manager"
    RISK_ANALYST = "risk_analyst"
    SUPPORT_AGENT = "support_agent"
    OPERATIONS_AGENT = "operations_agent"
    AUDITOR = "auditor"
    DEVELOPER_ADMIN = "developer_admin"


# Read-only roles: never allowed to mutate balances, KYC decisions, or card state.
READ_ONLY_ROLES = {
    AdminRole.SUPPORT_AGENT,
    AdminRole.AUDITOR,
    AdminRole.RISK_ANALYST,
}

# Roles allowed to approve/reject KYC submissions.
KYC_REVIEWER_ROLES = {
    AdminRole.SUPER_ADMIN,
    AdminRole.COMPLIANCE_OFFICER,
}

# Roles allowed to view the admin dashboard and transaction data.
DASHBOARD_VIEWER_ROLES = set(AdminRole)


def require_role(role: AdminRole, allowed: set[AdminRole]) -> None:
    if role not in allowed:
        raise ForbiddenError(f"Role '{role.value}' is not authorized for this action")

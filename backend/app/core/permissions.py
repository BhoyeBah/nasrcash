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

# Roles allowed to create/update fee and limit rules — a pricing/risk lever,
# not something support or auditors should be able to touch.
FEES_LIMITS_WRITE_ROLES = {
    AdminRole.SUPER_ADMIN,
    AdminRole.FINANCE_MANAGER,
}

# Roles allowed to see compliance alerts.
COMPLIANCE_VIEW_ROLES = {
    AdminRole.SUPER_ADMIN,
    AdminRole.COMPLIANCE_OFFICER,
    AdminRole.RISK_ANALYST,
    AdminRole.AUDITOR,
}

# Roles allowed to resolve/dismiss compliance alerts (a compliance decision).
COMPLIANCE_RESOLVE_ROLES = {
    AdminRole.SUPER_ADMIN,
    AdminRole.COMPLIANCE_OFFICER,
}


def require_role(role: AdminRole, allowed: set[AdminRole]) -> None:
    if role not in allowed:
        raise ForbiddenError(f"Role '{role.value}' is not authorized for this action")

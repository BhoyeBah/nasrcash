import csv
import io
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ConflictError, NotFoundError
from app.modules.audit.service import AuditService
from app.modules.auth.models import User, UserStatus
from app.modules.cards.models import Card
from app.modules.compliance.models import AlertSeverity, AlertStatus, AlertType, ComplianceAlert
from app.modules.notifications.models import NotificationType
from app.modules.notifications.service import NotificationService
from app.modules.payments.models import CardPayment, PaymentStatus
from app.modules.topups.models import Topup, TopupStatus
from app.modules.wallets.models import Wallet, WalletStatus
from app.modules.withdrawals.models import Withdrawal, WithdrawalStatus

# Weighted contribution of an open/reviewing alert to a user's aggregate risk
# score — a single CRITICAL alert is enough to cross the default auto-freeze
# threshold on its own; lower severities only add up through repetition.
SEVERITY_WEIGHTS = {
    AlertSeverity.LOW: 1,
    AlertSeverity.MEDIUM: 3,
    AlertSeverity.HIGH: 7,
    AlertSeverity.CRITICAL: 15,
}

OPEN_ALERT_STATUSES = (AlertStatus.OPEN.value, AlertStatus.REVIEWING.value)


class ComplianceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()
        self.audit = AuditService(db)
        self.notifications = NotificationService(db)

    async def _create_alert(
        self,
        user_id: uuid.UUID,
        alert_type: AlertType,
        severity: AlertSeverity,
        context: dict,
    ) -> ComplianceAlert:
        alert = ComplianceAlert(
            user_id=user_id,
            alert_type=alert_type.value,
            severity=severity.value,
            status=AlertStatus.OPEN.value,
            context=context,
        )
        self.db.add(alert)
        await self.db.flush()
        await self._maybe_auto_freeze(user_id)
        return alert

    async def check_large_transaction(
        self, user_id: uuid.UUID, amount: Decimal, transaction_type: str
    ) -> ComplianceAlert | None:
        threshold = Decimal(self.settings.compliance_large_transaction_threshold)
        if amount < threshold:
            return None

        if amount >= threshold * 10:
            severity = AlertSeverity.CRITICAL
        elif amount >= threshold * 3:
            severity = AlertSeverity.HIGH
        else:
            severity = AlertSeverity.MEDIUM
        return await self._create_alert(
            user_id,
            AlertType.LARGE_TRANSACTION,
            severity,
            context={
                "transaction_type": transaction_type,
                "amount": str(amount),
                "threshold": str(threshold),
            },
        )

    async def check_velocity(
        self, user_id: uuid.UUID, triggering_transaction_type: str
    ) -> ComplianceAlert | None:
        since = datetime.now(timezone.utc) - timedelta(
            minutes=self.settings.compliance_velocity_window_minutes
        )

        topup_count_result = await self.db.execute(
            select(func.count()).select_from(Topup).where(
                Topup.user_id == user_id,
                Topup.status == TopupStatus.SUCCESSFUL.value,
                Topup.confirmed_at >= since,
            )
        )
        withdrawal_count_result = await self.db.execute(
            select(func.count()).select_from(Withdrawal).where(
                Withdrawal.user_id == user_id,
                Withdrawal.status == WithdrawalStatus.SUCCESSFUL.value,
                Withdrawal.confirmed_at >= since,
            )
        )
        payment_count_result = await self.db.execute(
            select(func.count())
            .select_from(CardPayment)
            .join(Card, Card.id == CardPayment.card_id)
            .where(
                Card.user_id == user_id,
                CardPayment.status == PaymentStatus.SETTLED.value,
                CardPayment.created_at >= since,
            )
        )

        total = (
            topup_count_result.scalar_one()
            + withdrawal_count_result.scalar_one()
            + payment_count_result.scalar_one()
        )
        if total < self.settings.compliance_velocity_max_count:
            return None

        return await self._create_alert(
            user_id,
            AlertType.VELOCITY,
            AlertSeverity.MEDIUM,
            context={
                "triggering_transaction_type": triggering_transaction_type,
                "transaction_count": total,
                "window_minutes": self.settings.compliance_velocity_window_minutes,
                "threshold": self.settings.compliance_velocity_max_count,
            },
        )

    async def record_limit_breach(
        self, user_id: uuid.UUID, limit_type: str, context: dict
    ) -> ComplianceAlert:
        return await self._create_alert(
            user_id,
            AlertType.LIMIT_EXCEEDED_ATTEMPT,
            AlertSeverity.LOW,
            context={"limit_type": limit_type, **context},
        )

    # --- admin management ---

    async def list_alerts(
        self,
        status: str | None = None,
        severity: str | None = None,
        user_id: uuid.UUID | None = None,
    ) -> list[ComplianceAlert]:
        query = select(ComplianceAlert).order_by(ComplianceAlert.created_at.desc())
        if status is not None:
            query = query.where(ComplianceAlert.status == status)
        if severity is not None:
            query = query.where(ComplianceAlert.severity == severity)
        if user_id is not None:
            query = query.where(ComplianceAlert.user_id == user_id)
        result = await self.db.execute(query)
        return list(result.scalars())

    async def _transition(
        self,
        alert_id: uuid.UUID,
        new_status: AlertStatus,
        admin_id: uuid.UUID,
        resolution_notes: str | None,
    ) -> ComplianceAlert:
        alert = await self.db.get(ComplianceAlert, alert_id)
        if alert is None:
            raise NotFoundError("Alerte de conformité introuvable")
        if alert.status in {AlertStatus.RESOLVED.value, AlertStatus.DISMISSED.value}:
            raise ConflictError(f"Cette alerte est déjà '{alert.status}'")

        alert.status = new_status.value
        alert.resolved_at = datetime.now(timezone.utc)
        alert.resolved_by = admin_id
        alert.resolution_notes = resolution_notes
        await self.db.flush()
        return alert

    async def resolve_alert(
        self, alert_id: uuid.UUID, admin_id: uuid.UUID, resolution_notes: str | None
    ) -> ComplianceAlert:
        return await self._transition(alert_id, AlertStatus.RESOLVED, admin_id, resolution_notes)

    async def dismiss_alert(
        self, alert_id: uuid.UUID, admin_id: uuid.UUID, resolution_notes: str | None
    ) -> ComplianceAlert:
        return await self._transition(alert_id, AlertStatus.DISMISSED, admin_id, resolution_notes)

    # --- risk scoring & auto-freeze ---

    async def compute_risk_score(self, user_id: uuid.UUID) -> dict:
        since = datetime.now(timezone.utc) - timedelta(days=self.settings.compliance_risk_window_days)
        result = await self.db.execute(
            select(ComplianceAlert.severity, func.count()).where(
                ComplianceAlert.user_id == user_id,
                ComplianceAlert.status.in_(OPEN_ALERT_STATUSES),
                ComplianceAlert.created_at >= since,
            ).group_by(ComplianceAlert.severity)
        )
        breakdown = {severity: count for severity, count in result.all()}
        score = sum(
            SEVERITY_WEIGHTS[AlertSeverity(severity)] * count for severity, count in breakdown.items()
        )
        return {
            "user_id": user_id,
            "score": score,
            "alert_count": sum(breakdown.values()),
            "breakdown": breakdown,
            "window_days": self.settings.compliance_risk_window_days,
        }

    async def _maybe_auto_freeze(self, user_id: uuid.UUID) -> None:
        risk = await self.compute_risk_score(user_id)
        if risk["score"] < self.settings.compliance_risk_auto_freeze_threshold:
            return

        user = await self.db.get(User, user_id)
        if user is None or user.status == UserStatus.SUSPENDED.value:
            return  # already frozen — avoid duplicate audit entries/notifications

        user.status = UserStatus.SUSPENDED.value

        wallet_result = await self.db.execute(select(Wallet).where(Wallet.user_id == user_id))
        wallet = wallet_result.scalar_one_or_none()
        if wallet is not None:
            wallet.status = WalletStatus.BLOCKED.value

        await self.db.flush()
        await self.audit.log(
            actor_type="system", action="compliance.auto_freeze",
            target_type="user", target_id=str(user_id),
            context={"risk_score": risk["score"], "alert_count": risk["alert_count"]},
        )
        await self.notifications.create(
            user_id, NotificationType.SECURITY_ALERT.value,
            "Compte suspendu",
            "Votre compte a été temporairement suspendu suite à une activité suspecte. "
            "Contactez le support pour plus d'informations.",
        )

    async def unfreeze_user(self, user_id: uuid.UUID, admin_id: uuid.UUID) -> User:
        user = await self.db.get(User, user_id)
        if user is None:
            raise NotFoundError("Utilisateur introuvable")
        if user.status != UserStatus.SUSPENDED.value:
            raise ConflictError("Ce compte n'est pas suspendu")

        user.status = UserStatus.ACTIVE.value

        wallet_result = await self.db.execute(select(Wallet).where(Wallet.user_id == user_id))
        wallet = wallet_result.scalar_one_or_none()
        if wallet is not None and wallet.status == WalletStatus.BLOCKED.value:
            wallet.status = WalletStatus.ACTIVE.value

        await self.db.flush()
        await self.audit.log(
            actor_type="admin", actor_id=admin_id, action="compliance.manual_unfreeze",
            target_type="user", target_id=str(user_id),
        )
        return user

    # --- exportable report ---

    async def export_alerts_csv(
        self, since: datetime | None = None, until: datetime | None = None
    ) -> str:
        query = select(ComplianceAlert).order_by(ComplianceAlert.created_at.asc())
        if since is not None:
            query = query.where(ComplianceAlert.created_at >= since)
        if until is not None:
            query = query.where(ComplianceAlert.created_at <= until)
        result = await self.db.execute(query)
        alerts = list(result.scalars())

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["id", "user_id", "alert_type", "severity", "status", "created_at", "resolved_at", "resolved_by"]
        )
        for alert in alerts:
            writer.writerow([
                alert.id, alert.user_id, alert.alert_type, alert.severity, alert.status,
                alert.created_at.isoformat(), alert.resolved_at.isoformat() if alert.resolved_at else "",
                alert.resolved_by or "",
            ])
        return buffer.getvalue()

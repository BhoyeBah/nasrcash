import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.exceptions import ConflictError, NotFoundError
from app.modules.cards.models import Card
from app.modules.compliance.models import AlertSeverity, AlertStatus, AlertType, ComplianceAlert
from app.modules.payments.models import CardPayment, PaymentStatus
from app.modules.topups.models import Topup, TopupStatus
from app.modules.withdrawals.models import Withdrawal, WithdrawalStatus


class ComplianceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.settings = get_settings()

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
        return alert

    async def check_large_transaction(
        self, user_id: uuid.UUID, amount: Decimal, transaction_type: str
    ) -> ComplianceAlert | None:
        threshold = Decimal(self.settings.compliance_large_transaction_threshold)
        if amount < threshold:
            return None

        severity = AlertSeverity.HIGH if amount >= threshold * 3 else AlertSeverity.MEDIUM
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

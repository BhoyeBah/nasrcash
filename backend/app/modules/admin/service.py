import csv
import io
import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, UnauthorizedError, ValidationError
from app.core.permissions import AdminRole
from app.core.security import hash_secret, verify_secret
from app.modules.admin.models import AdminUser
from app.modules.auth.models import User
from app.modules.cards.models import Card
from app.modules.kyc.models import IN_FLIGHT_STATUSES, KycProfile
from app.modules.ledger.models import LedgerEntry
from app.modules.payments.models import CardPayment, PaymentStatus
from app.modules.topups.models import Topup, TopupStatus
from app.modules.wallets.models import Wallet


class AdminService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def authenticate(self, email: str, password: str) -> AdminUser:
        result = await self.db.execute(select(AdminUser).where(AdminUser.email == email))
        admin = result.scalar_one_or_none()
        if admin is None or not admin.is_active or not verify_secret(
            password, admin.password_hash
        ):
            raise UnauthorizedError("Email ou mot de passe invalide")
        return admin

    async def get_dashboard(self) -> dict:
        users_count = (
            await self.db.execute(select(func.count()).select_from(User))
        ).scalar_one()
        kyc_pending_count = (
            await self.db.execute(
                select(func.count())
                .select_from(KycProfile)
                .where(KycProfile.status.in_(IN_FLIGHT_STATUSES))
            )
        ).scalar_one()
        cards_count = (
            await self.db.execute(select(func.count()).select_from(Card))
        ).scalar_one()
        successful_topups_volume = (
            await self.db.execute(
                select(func.coalesce(func.sum(Topup.net_amount), 0)).where(
                    Topup.status == TopupStatus.SUCCESSFUL.value
                )
            )
        ).scalar_one()
        settled_payments_volume = (
            await self.db.execute(
                select(func.coalesce(func.sum(CardPayment.total_debited), 0)).where(
                    CardPayment.status == PaymentStatus.SETTLED.value
                )
            )
        ).scalar_one()
        declined_payments_count = (
            await self.db.execute(
                select(func.count())
                .select_from(CardPayment)
                .where(CardPayment.status == PaymentStatus.DECLINED.value)
            )
        ).scalar_one()
        revenue_total = (
            await self.db.execute(
                select(func.coalesce(func.sum(LedgerEntry.amount), 0)).where(
                    LedgerEntry.account_id == "revenue:nasrcash",
                    LedgerEntry.direction == "credit",
                )
            )
        ).scalar_one()
        total_wallet_balance = (
            await self.db.execute(
                select(func.coalesce(func.sum(Wallet.cached_available_balance), 0))
            )
        ).scalar_one()

        return {
            "users_count": users_count,
            "kyc_pending_count": kyc_pending_count,
            "cards_count": cards_count,
            "successful_topups_volume": Decimal(successful_topups_volume),
            "settled_payments_volume": Decimal(settled_payments_volume),
            "declined_payments_count": declined_payments_count,
            "revenue_total": Decimal(revenue_total),
            "total_wallet_cached_balance": Decimal(total_wallet_balance),
        }

    async def list_users(self, limit: int = 50, offset: int = 0) -> list[User]:
        result = await self.db.execute(
            select(User).order_by(User.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars())

    async def list_kyc_pending(self, limit: int = 50, offset: int = 0) -> list[KycProfile]:
        result = await self.db.execute(
            select(KycProfile)
            .where(KycProfile.status.in_(IN_FLIGHT_STATUSES))
            .order_by(KycProfile.submitted_at.asc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars())

    async def list_transactions(self, limit: int = 50, offset: int = 0) -> list[LedgerEntry]:
        result = await self.db.execute(
            select(LedgerEntry).order_by(LedgerEntry.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars())

    async def list_cards(self, limit: int = 50, offset: int = 0) -> list[Card]:
        result = await self.db.execute(
            select(Card).order_by(Card.created_at.desc()).limit(limit).offset(offset)
        )
        return list(result.scalars())

    # --- admin user (back-office account) management ---

    async def list_admin_users(self) -> list[AdminUser]:
        result = await self.db.execute(select(AdminUser).order_by(AdminUser.created_at.desc()))
        return list(result.scalars())

    async def create_admin_user(self, email: str, password: str, role: str) -> AdminUser:
        if role not in {r.value for r in AdminRole}:
            raise ValidationError(f"Rôle admin invalide : {role}")
        existing = await self.db.execute(select(AdminUser).where(AdminUser.email == email))
        if existing.scalar_one_or_none() is not None:
            raise ConflictError("Un compte admin existe déjà avec cet email")

        admin = AdminUser(email=email, password_hash=hash_secret(password), role=role)
        self.db.add(admin)
        await self.db.flush()
        return admin

    async def update_admin_role(self, admin_id: uuid.UUID, role: str) -> AdminUser:
        if role not in {r.value for r in AdminRole}:
            raise ValidationError(f"Rôle admin invalide : {role}")
        admin = await self.db.get(AdminUser, admin_id)
        if admin is None:
            raise NotFoundError("Compte admin introuvable")
        admin.role = role
        await self.db.flush()
        return admin

    async def set_admin_active(self, admin_id: uuid.UUID, is_active: bool) -> AdminUser:
        admin = await self.db.get(AdminUser, admin_id)
        if admin is None:
            raise NotFoundError("Compte admin introuvable")
        admin.is_active = is_active
        await self.db.flush()
        return admin

    # --- accounting export ---

    async def export_ledger_csv(
        self, since: datetime | None = None, until: datetime | None = None
    ) -> str:
        query = select(LedgerEntry).order_by(LedgerEntry.created_at.asc())
        if since is not None:
            query = query.where(LedgerEntry.created_at >= since)
        if until is not None:
            query = query.where(LedgerEntry.created_at <= until)
        result = await self.db.execute(query)
        entries = list(result.scalars())

        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            ["id", "ledger_transaction_id", "account_id", "direction", "amount", "currency", "created_at"]
        )
        for entry in entries:
            writer.writerow([
                entry.id, entry.ledger_transaction_id, entry.account_id, entry.direction,
                entry.amount, entry.currency, entry.created_at.isoformat(),
            ])
        return buffer.getvalue()

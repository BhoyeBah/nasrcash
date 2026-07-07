from decimal import Decimal
from typing import TypedDict

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import LedgerImbalanceError
from app.modules.ledger.models import EntryDirection, LedgerEntry, LedgerTransaction


class LedgerEntryInput(TypedDict):
    account_id: str
    direction: str  # "debit" | "credit"
    amount: Decimal
    currency: str
    description: str | None


class LedgerService:
    """The single source of truth for money movement in NasrCash.

    Every monetary operation — topup, card funding, international payment,
    refund — goes through ``record_transaction``. Account balances are never
    updated directly; they are always derived from this append-only log.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_transaction_by_reference(self, reference: str) -> LedgerTransaction | None:
        result = await self.db.execute(
            select(LedgerTransaction).where(LedgerTransaction.reference == reference)
        )
        return result.scalar_one_or_none()

    async def record_transaction(
        self,
        transaction_type: str,
        reference: str,
        entries: list[LedgerEntryInput],
        description: str | None = None,
    ) -> LedgerTransaction:
        existing = await self.get_transaction_by_reference(reference)
        if existing is not None:
            return existing

        if not entries:
            raise LedgerImbalanceError("A ledger transaction must have at least one entry")

        totals: dict[str, Decimal] = {}
        for entry in entries:
            sign = Decimal(1) if entry["direction"] == EntryDirection.CREDIT.value else Decimal(-1)
            totals[entry["currency"]] = totals.get(entry["currency"], Decimal(0)) + (
                sign * entry["amount"]
            )

        for currency, net in totals.items():
            if net != 0:
                raise LedgerImbalanceError(
                    f"Ledger transaction '{reference}' is unbalanced for {currency}: "
                    f"net={net}"
                )

        transaction = LedgerTransaction(
            transaction_type=transaction_type, reference=reference, description=description
        )
        self.db.add(transaction)
        await self.db.flush()

        for entry in entries:
            self.db.add(
                LedgerEntry(
                    ledger_transaction_id=transaction.id,
                    account_id=entry["account_id"],
                    direction=entry["direction"],
                    amount=entry["amount"],
                    currency=entry["currency"],
                    description=entry.get("description"),
                )
            )
        await self.db.flush()
        return transaction

    async def get_account_balance(self, account_id: str, currency: str) -> Decimal:
        """Recomputes the balance straight from the ledger — this is the
        authoritative value; any cached balance column is only a projection."""
        credit_sum = select(func.coalesce(func.sum(LedgerEntry.amount), 0)).where(
            LedgerEntry.account_id == account_id,
            LedgerEntry.currency == currency,
            LedgerEntry.direction == EntryDirection.CREDIT.value,
        )
        debit_sum = select(func.coalesce(func.sum(LedgerEntry.amount), 0)).where(
            LedgerEntry.account_id == account_id,
            LedgerEntry.currency == currency,
            LedgerEntry.direction == EntryDirection.DEBIT.value,
        )
        credits = (await self.db.execute(credit_sum)).scalar_one()
        debits = (await self.db.execute(debit_sum)).scalar_one()
        return Decimal(credits) - Decimal(debits)

    async def get_account_entries(
        self, account_id: str, limit: int = 50, offset: int = 0
    ) -> list[LedgerEntry]:
        result = await self.db.execute(
            select(LedgerEntry)
            .where(LedgerEntry.account_id == account_id)
            .order_by(LedgerEntry.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars())

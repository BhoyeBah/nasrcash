from decimal import Decimal

import pytest

from app.core.exceptions import LedgerImbalanceError
from app.modules.ledger.service import LedgerService


async def test_record_balanced_transaction_updates_balances(db_session):
    ledger = LedgerService(db_session)
    await ledger.record_transaction(
        transaction_type="TOPUP_SUCCESS",
        reference="topup-1",
        entries=[
            {
                "account_id": "provider:orange_money",
                "direction": "debit",
                "amount": Decimal("500000"),
                "currency": "GNF",
            },
            {
                "account_id": "wallet:11111111-1111-1111-1111-111111111111",
                "direction": "credit",
                "amount": Decimal("500000"),
                "currency": "GNF",
            },
        ],
    )

    wallet_balance = await ledger.get_account_balance(
        "wallet:11111111-1111-1111-1111-111111111111", "GNF"
    )
    provider_balance = await ledger.get_account_balance("provider:orange_money", "GNF")
    assert wallet_balance == Decimal("500000")
    assert provider_balance == Decimal("-500000")


async def test_unbalanced_transaction_is_rejected(db_session):
    ledger = LedgerService(db_session)
    with pytest.raises(LedgerImbalanceError):
        await ledger.record_transaction(
            transaction_type="BROKEN",
            reference="broken-1",
            entries=[
                {
                    "account_id": "wallet:aaa",
                    "direction": "credit",
                    "amount": Decimal("100"),
                    "currency": "GNF",
                },
                {
                    "account_id": "provider:orange_money",
                    "direction": "debit",
                    "amount": Decimal("99"),
                    "currency": "GNF",
                },
            ],
        )

    balance = await ledger.get_account_balance("wallet:aaa", "GNF")
    assert balance == Decimal("0")


async def test_replaying_same_reference_is_idempotent(db_session):
    ledger = LedgerService(db_session)
    entries = [
        {
            "account_id": "provider:orange_money",
            "direction": "debit",
            "amount": Decimal("1000"),
            "currency": "GNF",
        },
        {
            "account_id": "wallet:bbb",
            "direction": "credit",
            "amount": Decimal("1000"),
            "currency": "GNF",
        },
    ]

    first = await ledger.record_transaction("TOPUP_SUCCESS", "idem-1", entries)
    second = await ledger.record_transaction("TOPUP_SUCCESS", "idem-1", entries)

    assert first.id == second.id
    balance = await ledger.get_account_balance("wallet:bbb", "GNF")
    assert balance == Decimal("1000")


async def test_transaction_requires_at_least_one_entry(db_session):
    ledger = LedgerService(db_session)
    with pytest.raises(LedgerImbalanceError):
        await ledger.record_transaction("EMPTY", "empty-1", entries=[])


async def test_multi_currency_entries_are_balanced_per_currency(db_session):
    ledger = LedgerService(db_session)
    await ledger.record_transaction(
        transaction_type="CARD_PAYMENT_WITH_FX",
        reference="fx-1",
        entries=[
            {
                "account_id": "card:ccc",
                "direction": "debit",
                "amount": Decimal("92700"),
                "currency": "GNF",
            },
            {
                "account_id": "settlement:visa",
                "direction": "credit",
                "amount": Decimal("90000"),
                "currency": "GNF",
            },
            {
                "account_id": "revenue:nasrcash",
                "direction": "credit",
                "amount": Decimal("2700"),
                "currency": "GNF",
            },
        ],
    )

    assert await ledger.get_account_balance("card:ccc", "GNF") == Decimal("-92700")
    assert await ledger.get_account_balance("settlement:visa", "GNF") == Decimal("90000")
    assert await ledger.get_account_balance("revenue:nasrcash", "GNF") == Decimal("2700")

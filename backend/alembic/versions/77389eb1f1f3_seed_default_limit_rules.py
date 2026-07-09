"""seed default limit rules

Revision ID: 77389eb1f1f3
Revises: 3e6ee9b95773
Create Date: 2026-07-09 15:18:56.788298

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '77389eb1f1f3'
down_revision: Union[str, None] = '3e6ee9b95773'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


limit_rules_table = sa.table(
    "limit_rules",
    sa.column("id", sa.Uuid),
    sa.column("country_code", sa.String),
    sa.column("kyc_level", sa.Integer),
    sa.column("limit_type", sa.String),
    sa.column("max_amount", sa.Numeric),
    sa.column("max_count", sa.Integer),
    sa.column("is_active", sa.Boolean),
)

SEED_RULES = [
    {"limit_type": "topup_min", "max_amount": 1000},
    {"limit_type": "topup_max", "max_amount": 2000000},
    {"limit_type": "wallet_daily_topup_cap", "max_amount": 3000000},
    {"limit_type": "withdrawal_daily_cap", "max_amount": 2000000},
    {"limit_type": "max_cards_per_user", "max_count": 3},
    {"limit_type": "topup_max", "kyc_level": 2, "max_amount": 10000000},
    {"limit_type": "wallet_daily_topup_cap", "kyc_level": 2, "max_amount": 15000000},
    {"limit_type": "withdrawal_daily_cap", "kyc_level": 2, "max_amount": 10000000},
    {"limit_type": "card_payment_daily_cap", "kyc_level": 2, "max_amount": 5000000},
]


def upgrade() -> None:
    op.bulk_insert(
        limit_rules_table,
        [
            {
                "id": uuid.uuid4(),
                "country_code": rule.get("country_code"),
                "kyc_level": rule.get("kyc_level"),
                "limit_type": rule["limit_type"],
                "max_amount": rule.get("max_amount"),
                "max_count": rule.get("max_count"),
                "is_active": True,
            }
            for rule in SEED_RULES
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM limit_rules")

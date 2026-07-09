"""seed default fee rules

Revision ID: 9d398e0208d3
Revises: 06f477e6de04
Create Date: 2026-07-09 15:32:06.846591

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9d398e0208d3'
down_revision: Union[str, None] = '06f477e6de04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


fee_rules_table = sa.table(
    "fee_rules",
    sa.column("id", sa.Uuid),
    sa.column("country_code", sa.String),
    sa.column("provider_name", sa.String),
    sa.column("kyc_level", sa.Integer),
    sa.column("fee_type", sa.String),
    sa.column("rate", sa.Numeric),
    sa.column("fixed_amount", sa.Numeric),
    sa.column("is_active", sa.Boolean),
)

# Same values as the original MVP flat-rate settings, now data instead of code.
SEED_RULES = [
    {"fee_type": "topup", "rate": 0.02},
    {"fee_type": "withdrawal", "rate": 0.015},
    {"fee_type": "payment", "rate": 0.03},
]


def upgrade() -> None:
    op.bulk_insert(
        fee_rules_table,
        [
            {
                "id": uuid.uuid4(),
                "country_code": None,
                "provider_name": None,
                "kyc_level": None,
                "fee_type": rule["fee_type"],
                "rate": rule["rate"],
                "fixed_amount": 0,
                "is_active": True,
            }
            for rule in SEED_RULES
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM fee_rules")

"""seed pilot fx rates

Revision ID: 4a8fdc865d70
Revises: 348b00047977
Create Date: 2026-07-07 03:53:34.354178

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4a8fdc865d70'
down_revision: Union[str, None] = '348b00047977'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


fx_rates_table = sa.table(
    "fx_rates",
    sa.column("id", sa.Uuid),
    sa.column("base_currency", sa.String),
    sa.column("quote_currency", sa.String),
    sa.column("rate", sa.Numeric),
    sa.column("is_active", sa.Boolean),
)


def upgrade() -> None:
    op.bulk_insert(
        fx_rates_table,
        [
            {
                "id": uuid.uuid4(),
                "base_currency": "USD",
                "quote_currency": "GNF",
                "rate": 9000,
                "is_active": True,
            },
            {
                "id": uuid.uuid4(),
                "base_currency": "EUR",
                "quote_currency": "GNF",
                "rate": 9700,
                "is_active": True,
            },
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM fx_rates WHERE base_currency IN ('USD', 'EUR') AND quote_currency = 'GNF'")

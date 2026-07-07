"""seed pilot country data

Revision ID: 887e93b269d5
Revises: ad3605444ff1
Create Date: 2026-07-07 03:34:50.760474

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '887e93b269d5'
down_revision: Union[str, None] = 'ad3605444ff1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


countries_table = sa.table(
    "countries",
    sa.column("code", sa.String),
    sa.column("name", sa.String),
    sa.column("currency_code", sa.String),
    sa.column("phone_prefix", sa.String),
    sa.column("is_active", sa.Boolean),
)


def upgrade() -> None:
    op.bulk_insert(
        countries_table,
        [
            {
                "code": "GN",
                "name": "Guinée",
                "currency_code": "GNF",
                "phone_prefix": "+224",
                "is_active": True,
            }
        ],
    )


def downgrade() -> None:
    op.execute("DELETE FROM countries WHERE code = 'GN'")

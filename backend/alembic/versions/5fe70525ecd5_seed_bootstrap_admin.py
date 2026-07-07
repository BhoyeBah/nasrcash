"""seed bootstrap admin

Revision ID: 5fe70525ecd5
Revises: 38caffc76071
Create Date: 2026-07-07 04:03:20.520011

"""
import uuid
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5fe70525ecd5'
down_revision: Union[str, None] = '38caffc76071'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


admin_users_table = sa.table(
    "admin_users",
    sa.column("id", sa.Uuid),
    sa.column("email", sa.String),
    sa.column("password_hash", sa.String),
    sa.column("role", sa.String),
    sa.column("is_active", sa.Boolean),
)


def upgrade() -> None:
    from app.core.config import get_settings
    from app.core.security import hash_secret

    settings = get_settings()
    op.bulk_insert(
        admin_users_table,
        [
            {
                "id": uuid.uuid4(),
                "email": settings.admin_bootstrap_email,
                "password_hash": hash_secret(settings.admin_bootstrap_password),
                "role": "super_admin",
                "is_active": True,
            }
        ],
    )


def downgrade() -> None:
    from app.core.config import get_settings

    settings = get_settings()
    op.execute(
        sa.text("DELETE FROM admin_users WHERE email = :email").bindparams(
            email=settings.admin_bootstrap_email
        )
    )

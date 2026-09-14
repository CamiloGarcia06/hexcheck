"""crea __FEATURE__

Revision ID: __REV__
Revises: __DOWN_REV__
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "__REV__"
down_revision = __DOWN_REV__
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "__FEATURE__",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=200), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("__FEATURE__")

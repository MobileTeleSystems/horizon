# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
"""Add namespace_user table
Revision ID: 4c60578f3f1d
Revises: 09be8fd79dbc
Create Date: 2024-03-01 11:30:36.778975

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4c60578f3f1d"
down_revision = "09be8fd79dbc"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "namespace_user",
        sa.Column("namespace_id", sa.BigInteger(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("role", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(
            ["namespace_id"],
            ["namespace.id"],
            name=op.f("fk__namespace_user__namespace_id__namespace"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk__namespace_user__user_id__user"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("namespace_id", "user_id", name=op.f("pk__namespace_user")),
    )


def downgrade() -> None:
    op.drop_table("namespace_user")

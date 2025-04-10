# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

"""Add user table

Revision ID: b91de692624e
Revises:
Create Date: 2023-10-09 18:32:01.037500

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "b91de692624e"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=256), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__user")),
    )
    op.create_index(op.f("ix__user__username"), "user", ["username"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix__user__username"), table_name="user")
    op.drop_table("user")
    # ### end Alembic commands ###

# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
"""Add owner_id to namespace

Revision ID: 09be8fd79dbc
Revises: 2452f82ae06c
Create Date: 2024-02-29 11:22:25.802243

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "09be8fd79dbc"
down_revision = "2452f82ae06c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("namespace", sa.Column("owner_id", sa.BigInteger(), nullable=True))
    op.execute(
        """
        UPDATE namespace
        SET owner_id = changed_by_user_id
        WHERE owner_id IS NULL
        """,
    )
    op.alter_column("namespace", "owner_id", nullable=False)
    op.create_foreign_key(
        op.f("fk__namespace__owner_id__user"),
        "namespace",
        "user",
        ["owner_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.add_column("namespace_history", sa.Column("owner_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(
        op.f("fk__namespace_history__owner_id__user"),
        "namespace_history",
        "user",
        ["owner_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.execute(
        """
        INSERT INTO namespace_history (namespace_id, name, description, action, owner_id, changed_by_user_id)
        SELECT id, name, description, 'Set owner (automatic migration)', owner_id, NULL
        FROM namespace
        """,
    )


def downgrade() -> None:
    op.drop_constraint(op.f("fk__namespace_history__owner_id__user"), "namespace_history", type_="foreignkey")
    op.drop_column("namespace_history", "owner_id")
    op.drop_constraint(op.f("fk__namespace__owner_id__user"), "namespace", type_="foreignkey")
    op.drop_column("namespace", "owner_id")

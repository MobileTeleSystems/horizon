# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
"""Add namespace history

Revision ID: 5c7a5c5a193b
Revises: c2d6da81f9ec
Create Date: 2024-02-27 13:25:07.367475

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "5c7a5c5a193b"
down_revision = "c2d6da81f9ec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "namespace_history",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("namespace_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=2048), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("changed_by_user_id", sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(
            ["changed_by_user_id"],
            ["user.id"],
            name=op.f("fk__namespace_history__changed_by_user_id__user"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__namespace_history")),
    )
    op.create_index(op.f("ix__namespace_history__namespace_id"), "namespace_history", ["namespace_id"], unique=False)

    op.execute(
        """
        INSERT INTO namespace_history (namespace_id, name, description, action, changed_at, changed_by_user_id)
        SELECT id, name, description, 'Deleted', changed_at, changed_by_user_id
        FROM namespace
        WHERE is_deleted = TRUE
    """,
    )
    op.execute(
        """
        DELETE FROM namespace WHERE is_deleted = TRUE
    """,
    )
    op.drop_column("namespace", "is_deleted")


def downgrade() -> None:
    op.add_column(
        "namespace",
        sa.Column("is_deleted", sa.BOOLEAN(), autoincrement=False, nullable=False, server_default="FALSE"),
    )

    op.execute(
        """
        UPDATE namespace SET is_deleted = TRUE
        WHERE id IN (
            SELECT namespace_id FROM namespace_history WHERE action = 'Deleted'
        )
    """,
    )
    op.drop_index(op.f("ix__namespace_history__namespace_id"), table_name="namespace_history")
    op.drop_table("namespace_history")

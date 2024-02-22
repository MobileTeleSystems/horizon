# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
"""Add action to HWMHistory table

Revision ID: c2d6da81f9ec
Revises: 4bc3fffc0209
Create Date: 2024-02-22 15:47:40.155259

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import column, table

# revision identifiers, used by Alembic.
revision = "c2d6da81f9ec"
down_revision = "4bc3fffc0209"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("fk__hwm_history__hwm_id__hwm", "hwm_history", type_="foreignkey")
    op.add_column("hwm_history", sa.Column("action", sa.String(length=255), nullable=True))

    hwm_history_table = table("hwm_history", column("is_deleted", sa.Boolean), column("action", sa.String(length=255)))

    op.execute(
        hwm_history_table.update().where(hwm_history_table.c.is_deleted == sa.true()).values({"action": "Deleted"}),
    )
    op.execute(
        hwm_history_table.update().where(hwm_history_table.c.is_deleted == sa.false()).values({"action": "Updated"}),
    )

    op.execute(
        """
        WITH ranked_history AS (
            SELECT id, hwm_id, ROW_NUMBER() OVER(PARTITION BY hwm_id ORDER BY id ASC) AS rank
            FROM hwm_history
        )
        UPDATE hwm_history SET action = 'Created' WHERE id IN (
            SELECT id FROM ranked_history WHERE rank = 1
        );
    """,
    )
    op.execute("DELETE FROM hwm WHERE is_deleted = TRUE;")

    op.drop_column("hwm_history", "is_deleted")
    op.drop_column("hwm", "is_deleted")

    op.alter_column("hwm_history", "action", nullable=False)


def downgrade() -> None:
    op.add_column("hwm_history", sa.Column("is_deleted", sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.add_column("hwm", sa.Column("is_deleted", sa.BOOLEAN(), autoincrement=False, nullable=False))
    op.drop_column("hwm_history", "action")
    op.create_foreign_key("fk__hwm_history__hwm_id__hwm", "hwm_history", "hwm", ["hwm_id"], ["id"], ondelete="CASCADE")

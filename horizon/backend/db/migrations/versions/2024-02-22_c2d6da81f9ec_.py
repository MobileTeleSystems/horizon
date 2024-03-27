# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
"""Add action to HWMHistory table

Revision ID: c2d6da81f9ec
Revises: 4bc3fffc0209
Create Date: 2024-02-22 15:47:40.155259

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "c2d6da81f9ec"
down_revision = "4bc3fffc0209"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE hwm_history DROP CONSTRAINT fk__hwm_history__hwm_id__hwm")
    op.execute("ALTER TABLE hwm_history ADD COLUMN action VARCHAR(255)")

    op.execute("UPDATE hwm_history SET action = 'Deleted' WHERE is_deleted = TRUE")

    op.execute("UPDATE hwm_history SET action = 'Updated' WHERE is_deleted = FALSE")

    op.execute(
        """
        WITH ranked_history AS (
            SELECT id, hwm_id, ROW_NUMBER() OVER(PARTITION BY hwm_id ORDER BY id) AS rank
            FROM hwm_history
        )
        UPDATE hwm_history SET action = 'Created' WHERE id IN (
            SELECT id FROM ranked_history WHERE rank = 1
        )
    """,
    )
    op.execute("DELETE FROM hwm WHERE is_deleted = TRUE")

    op.execute("ALTER TABLE hwm_history DROP COLUMN is_deleted")
    op.execute("ALTER TABLE hwm DROP COLUMN is_deleted")
    op.execute("ALTER TABLE hwm_history ALTER COLUMN action SET NOT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE hwm_history ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE")
    op.execute("UPDATE hwm_history SET is_deleted = TRUE WHERE action = 'Deleted'")
    op.execute("ALTER TABLE hwm ADD COLUMN is_deleted BOOLEAN NOT NULL DEFAULT FALSE")
    op.execute("ALTER TABLE hwm_history DROP COLUMN action")
    op.execute(
        """
        ALTER TABLE hwm_history ADD CONSTRAINT fk__hwm_history__hwm_id__hwm
        FOREIGN KEY (hwm_id) REFERENCES hwm (id) ON DELETE CASCADE
    """,
    )

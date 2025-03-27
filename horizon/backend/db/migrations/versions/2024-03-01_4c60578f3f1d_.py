# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
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
        sa.Column("role", sa.String(length=50), nullable=False),
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
    # Any user who has changed a namespace at least once should be a maintainer
    op.execute(
        """
        INSERT INTO namespace_user (namespace_id, user_id, role)
            SELECT DISTINCT
                namespace_history.namespace_id,
                namespace_history.changed_by_user_id,
                'MAINTAINER' AS role
            FROM namespace_history
            JOIN namespace ON namespace_history.namespace_id = namespace.id
            WHERE
                namespace_history.changed_by_user_id IS NOT NULL
            AND namespace_history.changed_by_user_id != namespace.owner_id
        ON CONFLICT (namespace_id, user_id) DO NOTHING
        """,
    )
    # Any user who has changed any HWM in namespace at least once should be a developer
    op.execute(
        """
        INSERT INTO namespace_user (namespace_id, user_id, role)
            SELECT DISTINCT
                hwm_history.namespace_id,
                hwm_history.changed_by_user_id,
                'DEVELOPER' AS role
            FROM hwm_history
            JOIN namespace ON hwm_history.namespace_id = namespace.id
            WHERE
                hwm_history.changed_by_user_id IS NOT NULL
            AND hwm_history.changed_by_user_id != namespace.owner_id
        ON CONFLICT (namespace_id, user_id) DO NOTHING
        """,
    )


def downgrade() -> None:
    op.drop_table("namespace_user")

# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
"""Add is_admin to User

Revision ID: ec64f7b42221
Revises: 4c60578f3f1d
Create Date: 2024-03-18 15:59:19.680251

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ec64f7b42221"
down_revision = "4c60578f3f1d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("user", sa.Column("is_admin", sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    op.drop_column("user", "is_admin")

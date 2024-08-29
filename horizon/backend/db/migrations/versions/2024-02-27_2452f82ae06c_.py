# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
"""Drop is_deleted column from user

Revision ID: 2452f82ae06c
Revises: 5c7a5c5a193b
Create Date: 2024-02-27 14:55:54.744041

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "2452f82ae06c"
down_revision = "5c7a5c5a193b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('DELETE FROM "user" WHERE is_deleted = TRUE')
    op.drop_column("user", "is_deleted")


def downgrade() -> None:
    op.add_column("user", sa.Column("is_deleted", sa.BOOLEAN(), autoincrement=False, nullable=False))

# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
"""Increase HWM name limit

Revision ID: 4bc3fffc0209
Revises: dfce9f35c00e
Create Date: 2023-12-23 12:34:38.843814

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "4bc3fffc0209"
down_revision = "dfce9f35c00e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "hwm",
        "name",
        existing_type=sa.VARCHAR(length=256),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )
    op.alter_column(
        "hwm_history",
        "name",
        existing_type=sa.VARCHAR(length=256),
        type_=sa.String(length=2048),
        existing_nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "hwm_history",
        "name",
        existing_type=sa.String(length=2048),
        type_=sa.VARCHAR(length=256),
        existing_nullable=False,
    )
    op.alter_column(
        "hwm",
        "name",
        existing_type=sa.String(length=2048),
        type_=sa.VARCHAR(length=256),
        existing_nullable=False,
    )
    # ### end Alembic commands ###
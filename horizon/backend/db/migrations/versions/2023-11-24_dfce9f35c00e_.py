# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
"""Add credentials_cache table

Revision ID: dfce9f35c00e
Revises: 6b9001985cd2
Create Date: 2023-11-24 12:45:37.006395

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "dfce9f35c00e"
down_revision = "6b9001985cd2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "credentials_cache",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("login", sa.String(length=256), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
            name=op.f("fk__credentials_cache__user_id__user"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__credentials_cache")),
    )
    op.create_index(op.f("ix__credentials_cache__login"), "credentials_cache", ["login"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix__credentials_cache__login"), table_name="credentials_cache")
    op.drop_table("credentials_cache")
    # ### end Alembic commands ###
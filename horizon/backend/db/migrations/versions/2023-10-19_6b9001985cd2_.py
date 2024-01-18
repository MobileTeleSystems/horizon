# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
"""Add hwm_history table

Revision ID: 6b9001985cd2
Revises: edd2e353ca38
Create Date: 2023-10-19 14:48:41.934231

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "6b9001985cd2"
down_revision = "edd2e353ca38"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "hwm_history",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("hwm_id", sa.BigInteger(), nullable=True),
        sa.Column("namespace_id", sa.BigInteger(), nullable=True),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("entity", sa.Text(), nullable=True),
        sa.Column("expression", sa.Text(), nullable=True),
        sa.Column("changed_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("changed_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["changed_by_user_id"],
            ["user.id"],
            name=op.f("fk__hwm_history__changed_by_user_id__user"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["hwm_id"], ["hwm.id"], name=op.f("fk__hwm_history__hwm_id__hwm"), ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["namespace_id"],
            ["namespace.id"],
            name=op.f("fk__hwm_history__namespace_id__namespace"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__hwm_history")),
    )
    op.create_index(op.f("ix__hwm_history__hwm_id"), "hwm_history", ["hwm_id"], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix__hwm_history__hwm_id"), table_name="hwm_history")
    op.drop_table("hwm_history")
    # ### end Alembic commands ###

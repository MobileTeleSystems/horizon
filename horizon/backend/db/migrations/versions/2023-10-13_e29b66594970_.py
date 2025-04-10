# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
"""Add namespace table

Revision ID: e29b66594970
Revises: b91de692624e
Create Date: 2023-10-13 12:24:06.942579

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "e29b66594970"
down_revision = "b91de692624e"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "namespace",
        sa.Column("id", sa.BigInteger(), nullable=False),
        sa.Column("name", sa.String(length=256), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            server_onupdate=sa.text("now()"),  # type: ignore[arg-type]
            nullable=False,
        ),
        sa.Column("changed_by_user_id", sa.BigInteger(), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["changed_by_user_id"],
            ["user.id"],
            name=op.f("fk__namespace__changed_by_user_id__user"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk__namespace")),
    )
    op.create_index(op.f("ix__namespace__name"), "namespace", ["name"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix__namespace__name"), table_name="namespace")
    op.drop_table("namespace")
    # ### end Alembic commands ###

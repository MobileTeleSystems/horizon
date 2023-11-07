# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from sqlalchemy import JSON, BigInteger, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from horizon.db.mixins.changed_by import ChangedByMixin
from horizon.db.mixins.deletable import DeletableMixin
from horizon.db.models.base import Base
from horizon.db.models.namespace import Namespace


class HWM(Base, ChangedByMixin, DeletableMixin):
    __tablename__ = "hwm"
    __table_args__ = (UniqueConstraint("namespace_id", "name", name="hwm_name_unique_per_namespace"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    namespace_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("namespace.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    namespace = relationship(Namespace, lazy="selectin")

    name: Mapped[str] = mapped_column(String(256), nullable=False, index=True)  # noqa: WPS432
    description: Mapped[str] = mapped_column(Text(), nullable=False, default="")
    type: Mapped[str] = mapped_column(String(64), nullable=False)  # noqa: WPS432
    value: Mapped[str] = mapped_column(JSON(), nullable=False)
    entity: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    expression: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

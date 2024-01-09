# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from sqlalchemy import JSON, BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from horizon.backend.db.mixins.changed_by import ChangedByMixin
from horizon.backend.db.mixins.deletable import DeletableMixin
from horizon.backend.db.models.base import Base


class HWMHistory(Base, ChangedByMixin, DeletableMixin):
    __tablename__ = "hwm_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    hwm_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("hwm.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    namespace_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("namespace.id", ondelete="CASCADE"),
        nullable=True,
    )

    name: Mapped[str] = mapped_column(String(2048), nullable=False)  # noqa: WPS432
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False)  # noqa: WPS432
    value: Mapped[str] = mapped_column(JSON(), nullable=False)
    entity: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)
    expression: Mapped[Optional[str]] = mapped_column(Text(), nullable=True)

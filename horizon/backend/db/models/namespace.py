# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from sqlalchemy import BigInteger, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from horizon.backend.db.mixins.changed_by import ChangedByMixin
from horizon.backend.db.mixins.deletable import DeletableMixin
from horizon.backend.db.models.base import Base


class Namespace(Base, ChangedByMixin, DeletableMixin):
    __tablename__ = "namespace"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(
        String(256),  # noqa: WPS432
        nullable=False,
        unique=True,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
    )

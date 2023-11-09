# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from horizon.backend.db.mixins.deletable import DeletableMixin
from horizon.backend.db.mixins.timestamp import TimestampMixin
from horizon.backend.db.models.base import Base


class User(Base, TimestampMixin, DeletableMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(256),  # noqa: WPS432
        nullable=False,
        unique=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

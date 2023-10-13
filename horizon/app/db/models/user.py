# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.mixins.autorepr import AutoreprMixin
from app.db.mixins.deletable import DeletableMixin
from app.db.mixins.timestamp import TimestampMixin
from app.db.models.base import Base


class User(Base, AutoreprMixin, TimestampMixin, DeletableMixin):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str] = mapped_column(
        String(256),  # noqa: WPS432
        nullable=False,
        unique=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

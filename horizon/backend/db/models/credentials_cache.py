# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from horizon.backend.db.mixins.timestamp import TimestampMixin
from horizon.backend.db.models.base import Base
from horizon.backend.db.models.user import User


class CredentialsCache(Base, TimestampMixin):
    __tablename__ = "credentials_cache"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # Same user can have multiple credentials (e.g. name+password, email+password)
    # So this field is named `login` instead of `username`
    login: Mapped[str] = mapped_column(
        String(256),  # noqa: WPS432
        nullable=False,
        unique=True,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(
        Text(),
        nullable=False,
    )

    user = relationship(User, lazy="selectin")

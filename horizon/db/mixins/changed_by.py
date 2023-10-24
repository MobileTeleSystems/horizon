# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime, timezone
from functools import partial

from sqlalchemy import BigInteger, DateTime, ForeignKey, func
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column, relationship

from horizon.db.models.user import User


class ChangedByMixin:
    changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=partial(datetime.now, tz=timezone.utc),
        nullable=False,
    )
    changed_by_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )

    @declared_attr
    def changed_by_user(cls):
        return relationship(User, lazy="selectin")

    @declared_attr
    def changed_by(cls):
        return association_proxy("changed_by_user", "username")

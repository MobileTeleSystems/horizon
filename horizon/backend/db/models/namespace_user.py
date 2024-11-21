# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from horizon.backend.db.models.base import Base


class NamespaceUser(Base):
    __tablename__ = "namespace_user"

    namespace_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("namespace.id", ondelete="CASCADE"),
        primary_key=True,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(
        String(50),  # noqa: WPS432
        nullable=False,
    )

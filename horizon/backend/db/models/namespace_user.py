# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from sqlalchemy import BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy_utils import ChoiceType

from horizon.backend.db.models.base import Base
from horizon.commons.dto.role import Role


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
    role: Mapped[Role] = mapped_column(
        ChoiceType(Role),
        nullable=False,
    )

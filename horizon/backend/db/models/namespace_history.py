# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from horizon.backend.db.mixins.changed_by import ChangedByMixin
from horizon.backend.db.models.base import Base


class NamespaceHistory(Base, ChangedByMixin):
    __tablename__ = "namespace_history"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    namespace_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=True)

    name: Mapped[str] = mapped_column(String(2048), nullable=False)  # noqa: WPS432
    description: Mapped[str] = mapped_column(Text(), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)  # noqa: WPS432
    owner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )
    owner = relationship("User", foreign_keys=[owner_id])
    owned_by: AssociationProxy[str] = association_proxy("owner", "username")

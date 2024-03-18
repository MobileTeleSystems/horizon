# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from enum import IntEnum

from sqlalchemy import BigInteger, ForeignKey, String, Text
from sqlalchemy.ext.associationproxy import AssociationProxy, association_proxy
from sqlalchemy.orm import Mapped, mapped_column, relationship

from horizon.backend.db.mixins.changed_by import ChangedByMixin
from horizon.backend.db.models.base import Base


class NamespaceUserRoleInt(IntEnum):
    GUEST = 0
    DEVELOPER = 1
    MAINTAINER = 2
    OWNER = 3


class Namespace(Base, ChangedByMixin):
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
    owner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("user.id", ondelete="RESTRICT"),
        nullable=False,
    )
    owner = relationship("User", foreign_keys=[owner_id])
    owned_by: AssociationProxy[str] = association_proxy("owner", "username")

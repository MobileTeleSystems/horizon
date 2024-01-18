# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column


class DeletableMixin:
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

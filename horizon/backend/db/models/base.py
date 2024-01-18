# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from sqlalchemy import MetaData, inspect
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy_utils import generic_repr

convention = {
    "all_column_names": lambda constraint, table: "_".join(
        [column.name for column in constraint.columns.values()],
    ),
    "ix": "ix__%(table_name)s__%(all_column_names)s",
    "uq": "uq__%(table_name)s__%(all_column_names)s",
    "ck": "ck__%(table_name)s__%(constraint_name)s",
    "fk": ("fk__%(table_name)s__%(all_column_names)s__" "%(referred_table_name)s"),
    "pk": "pk__%(table_name)s",
}

horizon_metadata = MetaData(naming_convention=convention)  # type: ignore


@generic_repr
class Base(DeclarativeBase):
    metadata = horizon_metadata

    def to_dict(self, exclude: set[str] | None = None):
        exclude = exclude or set()
        return {c.key: getattr(self, c.key) for c in inspect(self).mapper.column_attrs if c.key not in exclude}

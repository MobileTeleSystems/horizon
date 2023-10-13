# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0


from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

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


class Base(DeclarativeBase):
    metadata = horizon_metadata

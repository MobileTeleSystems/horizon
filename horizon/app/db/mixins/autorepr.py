# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0


class AutoreprMixin:
    def __repr__(self) -> str:
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}  # type: ignore[attr-defined]
        data_str = ", ".join(f"{key}={value!r}" for key, value in data.items())
        type_name = type(self).__name__
        return f"{type_name}({data_str})"

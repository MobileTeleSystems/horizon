# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import ClassVar, Optional


class Unset:  # noqa: WPS600
    _instance: ClassVar[Optional[Unset]] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __len__(self):
        # handle ``min_length`` validator
        return 1

    def __repr__(self):
        return "Unset()"

    def __str__(self):
        return "<unset>"

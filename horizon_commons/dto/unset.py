# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Optional


@dataclass
class Unset(str):  # noqa: WPS600
    _instance: ClassVar[Optional[Unset]] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, "<unset>")
        return cls._instance

    def __repr__(self):
        return "<unset>"

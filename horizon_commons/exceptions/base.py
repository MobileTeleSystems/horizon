# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Any


class ApplicationError(ABC, Exception):
    @property
    @abstractmethod
    def message(self) -> str:
        ...

    @property
    @abstractmethod
    def details(self) -> Any:
        ...

    def __str__(self) -> str:
        return self.message

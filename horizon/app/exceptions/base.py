# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from abc import abstractmethod
from typing import Any


class ApplicationError(Exception):
    @property
    @abstractmethod
    def message(self) -> str:
        ...

    @property
    @abstractmethod
    def details(self) -> Any:
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}: {self.message}"

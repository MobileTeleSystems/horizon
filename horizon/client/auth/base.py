# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, TypeVar

if TYPE_CHECKING:
    from pydantic import AnyHttpUrl

Session = TypeVar("Session", bound=Any)


class BaseAuth(ABC):
    """
    Base authentication class.
    """

    type: str

    @abstractmethod
    def patch_session(self, session: Session) -> Session:
        """Get session object and return it with necessary patches applied"""
        ...

    @abstractmethod
    def fetch_token_kwargs(self, base_url: AnyHttpUrl) -> dict[str, Any]:
        """Return key-values arguments for ``client.fetch_token(...)`` method.

        Empty dict means that this method should not be called.
        """
        ...

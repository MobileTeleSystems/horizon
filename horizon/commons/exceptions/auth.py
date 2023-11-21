# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from horizon.commons.exceptions.base import ApplicationError


class AuthorizationError(ApplicationError):
    """Authorization request is failed.

    Examples
    --------

    .. code-block:: python

        raise AuthorizationError("User 'test' is disabled")

    """

    def __init__(self, message: str, details: Any = None) -> None:
        self._message = message
        self._details = details

    @property
    def message(self) -> str:
        return self._message

    @property
    def details(self) -> Any:
        return self._details

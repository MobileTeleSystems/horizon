# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from horizon.commons.exceptions.base import ApplicationError


class SetupError(ApplicationError):
    """Application setup is failed.

    Examples
    --------

    .. code-block:: python

        raise SetupError("Application is not set up properly")
    """

    def __init__(self, message: str, details: Any = None) -> None:
        self._message = message
        self._details = details

    @property
    def message(self) -> str:
        return self._message

    @property
    def details(self) -> None:
        return self._details

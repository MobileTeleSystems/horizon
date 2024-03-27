# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from horizon.commons.exceptions.base import ApplicationError


class BadRequestError(ApplicationError):
    """Bad request error.

    This exception should be raised when a request cannot be processed due to
    client-side errors (e.g., invalid data, duplicate entries).

    Examples
    --------

    >>> from horizon.commons.exceptions import BadRequestError
    >>> raise BadRequestError("Duplicate username detected. Each username must appear only once.")
    Traceback (most recent call last):
    horizon.commons.exceptions.BadRequestError: Duplicate username detected. Each username must appear only once.
    """

    reason: str
    """Bad request reason message"""

    def __init__(self, reason: str):
        self.reason = reason

    @property
    def message(self) -> str:
        return self.reason

    @property
    def details(self) -> dict:
        return {}

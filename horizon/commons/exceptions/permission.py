# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any

from horizon.commons.exceptions.base import ApplicationError


class PermissionDeniedError(ApplicationError):
    """
    Permission denied for performing the requested action.

    Examples
    --------

    >>> from horizon.commons.exceptions import PermissionDeniedError
    >>> raise PermissionDeniedError(required_role="DEVELOPER", actual_role="GUEST")
    Traceback (most recent call last):
    horizon.commons.exceptions.PermissionDeniedError: Permission denied. User has role GUEST but action requires at least DEVELOPER.
    """  # noqa: E501

    required_role: str
    """Required role to perform action"""

    actual_role: str
    """Actual user role"""

    def __init__(self, required_role: str, actual_role: str):
        self.required_role = required_role
        self.actual_role = actual_role

    @property
    def message(self) -> str:
        return f"Permission denied. User has role {self.actual_role} but action requires at least {self.required_role}."

    @property
    def details(self) -> dict[str, Any]:
        return {
            "required_role": self.required_role,
            "actual_role": self.actual_role,
        }

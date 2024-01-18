# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any

from horizon.commons.exceptions.base import ApplicationError


class EntityNotFoundError(ApplicationError):
    """Entity not found.

    Examples
    --------

    .. code-block:: python

        raise EntityNotFoundError("User", "username", "test")
    """

    entity_type: str
    """Entity type"""

    field: str
    """Entity identifier field"""

    value: Any
    """Entity identifier value"""

    def __init__(self, entity_type: str, field: str, value: Any):
        self.entity_type = entity_type
        self.field = field
        self.value = value

    @property
    def message(self) -> str:
        if self.field is not None:
            return f"{self.entity_type} with {self.field}={self.value!r} not found"
        return f"{self.entity_type} not found"

    @property
    def details(self) -> dict[str, Any]:
        return {
            "entity_type": self.entity_type,
            "field": self.field,
            "value": self.value,
        }


class EntityAlreadyExistsError(ApplicationError):
    """Entity with same identifier already exists.

    Examples
    --------

    .. code-block:: python

        raise EntityAlreadyExistsError("User", "username", "test")
    """

    entity_type: str
    """Entity type"""

    field: str
    """Entity identifier field"""

    value: Any
    """Entity identifier value"""

    def __init__(self, entity_type: str, field: str, value: Any):
        self.entity_type = entity_type
        self.field = field
        self.value = value

    @property
    def message(self) -> str:
        return f"{self.entity_type} with {self.field}={self.value!r} already exists"

    @property
    def details(self) -> dict[str, Any]:
        return {
            "entity_type": self.entity_type,
            "field": self.field,
            "value": self.value,
        }

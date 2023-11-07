# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import Any

from horizon_commons.exceptions.base import ApplicationError


class EntityNotFoundError(ApplicationError):
    def __init__(
        self,
        entity_type: str,
        field: str | None = None,
        value: Any | None = None,
    ):
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


class EntityInvalidError(ApplicationError):
    def __init__(self, entity_type: str, field: str, value: Any):
        self.entity_type = entity_type
        self.field = field
        self.value = value

    @property
    def message(self) -> str:
        return f"{self.entity_type} has wrong {self.field!r} value {self.value!r}"

    @property
    def details(self) -> dict[str, Any]:
        return {
            "entity_type": self.entity_type,
            "field": self.field,
            "value": self.value,
        }

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Any

from app.exceptions.base import ApplicationError


class EntityNotFoundError(ApplicationError):
    def __init__(
        self,
        entity_type: type,
        field: str | None = None,
        value: Any | None = None,
    ):
        self.entity_type = entity_type
        self.field = field
        self.value = value

    @property
    def message(self) -> str:
        if self.field is not None:
            return f"{self.entity_type.__name__} with {self.field}={self.value!r} not found"
        return f"{self.entity_type.__name__} not found"

    @property
    def details(self) -> dict[str, Any]:
        return {
            "entity_type": self.entity_type.__name__,
            "field": self.field,
            "value": self.value,
        }


class EntityAlreadyExistsError(ApplicationError):
    def __init__(self, entity_type: type, field: str, value: Any):
        self.entity_type = entity_type
        self.field = field
        self.value = value

    @property
    def message(self) -> str:
        return f"{self.entity_type.__name__} with {self.field}={self.value!r} already exist"

    @property
    def details(self) -> dict[str, Any]:
        return {
            "entity_type": self.entity_type.__name__,
            "field": self.field,
            "value": self.value,
        }

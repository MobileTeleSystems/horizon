# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime

from pydantic import BaseModel, Field, root_validator

from horizon_commons.dto import Unset
from horizon_commons.schemas.v1.pagination import PaginateQueryV1


class NamespaceResponseV1(BaseModel):
    """Namespace response."""

    id: int
    name: str
    description: str
    changed_at: datetime
    changed_by: str | None = None

    class Config:
        orm_mode = True


class NamespacePaginateQueryV1(PaginateQueryV1):
    """Query params for namespace pagination request."""

    # more arguments can be added in future


class NamespaceCreateRequestV1(BaseModel):
    """Request body for namespace creation request."""

    name: str = Field(min_length=1)
    description: str = ""


class NamespaceUpdateRequestV1(BaseModel):
    """Request body for namespace update request.

    If some field is not provided, it will not be updated.
    """

    name: str | Unset = Field(default=Unset(), min_length=1)
    description: str | Unset = Unset()

    @root_validator
    def _any_field_set(cls, values):
        """Validate that at least one field is set."""
        values_set = {k for k, v in values.items() if not isinstance(v, Unset)}
        if not values_set:
            raise ValueError("At least one field must be set.")
        return values

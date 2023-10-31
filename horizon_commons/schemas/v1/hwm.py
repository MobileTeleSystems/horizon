# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, root_validator

from horizon_commons.dto import Unset
from horizon_commons.schemas.v1.pagination import PaginateQueryV1


class HWMResponseV1(BaseModel):
    """HWM response."""

    id: int
    name: str
    description: str
    type: str
    value: Any
    entity: str | None = None
    expression: str | None = None
    changed_at: datetime
    changed_by: str | None = None

    class Config:
        orm_mode = True


class HWMPaginateQueryV1(PaginateQueryV1):
    """Query params for HWM pagination request."""

    # more arguments can be added in future


class HWMWriteRequestV1(BaseModel):
    """Request body for HWM write request.

    If HWM does not exist, it will be created. If does, it will be updated.

    If some field is not provided, it will not be updated.
    """

    description: str | Unset = Unset()
    type: str | Unset = Field(default=Unset(), min_length=1)
    value: Any | Unset = Unset()
    entity: str | None | Unset = Unset()
    expression: str | None | Unset = Unset()

    @root_validator
    def _any_field_set(cls, values):
        """Validate that at least one field is set."""
        values_set = {k for k, v in values.items() if not isinstance(v, Unset)}
        if not values_set:
            raise ValueError("At least one field must be set.")
        return values

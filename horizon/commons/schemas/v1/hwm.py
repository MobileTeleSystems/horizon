# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from typing import Any, Optional, Union

from pydantic import BaseModel, Field, root_validator

from horizon.commons.dto import Unset
from horizon.commons.schemas.v1.pagination import PaginateQueryV1

MAX_NAME_LENGTH = 2048
MAX_TYPE_LENGTH = 64


class HWMResponseV1(BaseModel):
    """HWM response."""

    id: int = Field(description="HWM id")
    namespace_id: int = Field(description="Namespace id HWM is bound to")
    name: str = Field(description="HWM name, unique in the namespace")
    description: str = Field(description="HWM description")
    type: str = Field(description="HWM type, any non-empty string")
    value: Any = Field(description="HWM value, any JSON serializable value")
    entity: Optional[str] = Field(default=None, description="Name of entity associated with the HWM. Can be any string")
    expression: Optional[str] = Field(
        default=None,
        description="Expression used to calculate HWM value. Can be any string",
    )
    changed_at: datetime = Field(description="Timestamp of last change of the HWM data")
    changed_by: Optional[str] = Field(default=None, description="Latest user who changed the HWM data")

    class Config:
        # pydantic v1
        orm_mode = True
        # pydantic v2
        from_attributes = True


class HWMPaginateQueryV1(PaginateQueryV1):
    """Query params for HWM pagination request."""

    namespace_id: int
    name: Optional[str] = Field(default=None, min_length=1, max_length=MAX_NAME_LENGTH)

    # more arguments can be added in future


class HWMCreateRequestV1(BaseModel):
    """Request body for HWM create request."""

    namespace_id: int
    name: str = Field(min_length=1, max_length=MAX_NAME_LENGTH)
    description: str = ""
    type: str = Field(min_length=1, max_length=MAX_TYPE_LENGTH)
    value: Any
    entity: Optional[str] = None
    expression: Optional[str] = None


class HWMUpdateRequestV1(BaseModel):
    """Request body for HWM update request.

    If field value is not set, it will not be updated.
    """

    name: Union[str, Unset] = Field(default=Unset(), min_length=1, max_length=MAX_NAME_LENGTH)
    description: Union[str, Unset] = Unset()
    type: Union[str, Unset] = Field(default=Unset(), min_length=1, max_length=MAX_TYPE_LENGTH)
    value: Union[Any, Unset] = Unset()
    entity: Union[str, None, Unset] = Unset()
    expression: Union[str, None, Unset] = Unset()

    class Config:
        arbitrary_types_allowed = True

    @root_validator(skip_on_failure=True)
    def _any_field_set(cls, values):
        """Validate that at least one field is set."""
        values_set = {k for k, v in values.items() if not isinstance(v, Unset)}
        if not values_set:
            raise ValueError("At least one field must be set.")
        return values

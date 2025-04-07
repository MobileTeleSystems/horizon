# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, root_validator, validator
from pydantic import __version__ as pydantic_version

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
        if pydantic_version >= "2":
            from_attributes = True
        else:
            orm_mode = True


class HWMListResponseV1(BaseModel):
    hwms: List[HWMResponseV1]


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

    name: str = Field(default=Unset(), min_length=1, max_length=MAX_NAME_LENGTH)  # type: ignore[assignment]
    description: str = Unset()  # type: ignore[assignment]
    type: str = Field(default=Unset(), min_length=1, max_length=MAX_TYPE_LENGTH)  # type: ignore[assignment]
    value: Any = Unset()  # type: ignore[assignment]
    entity: Optional[str] = Unset()  # type: ignore[assignment]
    expression: Optional[str] = Unset()  # type: ignore[assignment]

    class Config:
        arbitrary_types_allowed = True

    @root_validator(skip_on_failure=True)
    def _any_field_set(cls, values):  # noqa: N805
        """Validate that at least one field is set."""
        values_set = {k for k, v in values.items() if not isinstance(v, Unset)}
        if not values_set:
            msg = "At least one field must be set."
            raise ValueError(msg)
        return values


class HWMBulkCopyRequestV1(BaseModel):
    """Schema for request body of HWM copy operation."""

    source_namespace_id: int = Field(description="Source namespace ID from which HWMs are copied.")
    target_namespace_id: int = Field(description="Target namespace ID to which HWMs are copied.")
    hwm_ids: List[int] = Field(description="List of HWM IDs to be copied.")
    with_history: bool = Field(default=False, description="Whether to copy HWM history.")

    @validator("hwm_ids", pre=True, always=True)
    def _check_hwm_ids_not_empty(cls, v):  # noqa: N805
        if not len(v):
            msg = "List should have at least 1 item after validation, not 0"
            raise ValueError(msg)
        return v

    @root_validator(skip_on_failure=True)
    def _check_namespace_ids(cls, values):  # noqa: N805
        """Validator to ensure source and target namespace IDs are different."""
        source_namespace_id, target_namespace_id = values.get("source_namespace_id"), values.get("target_namespace_id")
        if source_namespace_id == target_namespace_id:
            msg = "Source and target namespace IDs must not be the same."
            raise ValueError(msg)
        return values


class HWMBulkDeleteRequestV1(BaseModel):
    """Schema for request body of bulk delete HWM operation."""

    namespace_id: int
    hwm_ids: List[int]

    @validator("hwm_ids", pre=True, always=True)
    def _check_hwm_ids_not_empty(cls, v):  # noqa: N805
        if not len(v):
            msg = "List should have at least 1 item after validation, not 0"
            raise ValueError(msg)
        return v

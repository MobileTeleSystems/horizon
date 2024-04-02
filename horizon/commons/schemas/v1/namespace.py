# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field
from pydantic import __version__ as pydantic_version
from pydantic import root_validator

from horizon.commons.dto import Unset
from horizon.commons.schemas.v1.pagination import PaginateQueryV1

MAX_NAME_LENGTH = 256


class NamespaceUserRole(str, Enum):  # noqa: WPS60
    DEVELOPER = "DEVELOPER"
    MAINTAINER = "MAINTAINER"
    OWNER = "OWNER"


class NamespaceResponseV1(BaseModel):
    """Namespace response."""

    id: int = Field(description="Namespace id")
    name: str = Field(description="Namespace name, unique in the entire database")
    description: str = Field(description="Namespace description")
    owned_by: str = Field(description="The namespace owner")
    changed_at: datetime = Field(description="Timestamp of last change of the namespace data")
    changed_by: Optional[str] = Field(default=None, description="Latest user who changed the namespace data")

    class Config:
        if pydantic_version >= "2":
            from_attributes = True
        else:
            orm_mode = True


class NamespacePaginateQueryV1(PaginateQueryV1):
    """Query params for namespace pagination request."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=MAX_NAME_LENGTH)

    # more arguments can be added in future


class NamespaceCreateRequestV1(BaseModel):
    """Request body for namespace creation request."""

    name: str = Field(min_length=1, max_length=MAX_NAME_LENGTH)
    description: str = ""


class NamespaceUpdateRequestV1(BaseModel):
    """Request body for namespace update request.

    If field value is not set, it will not be updated.
    """

    name: Union[str, Unset] = Field(default=Unset(), min_length=1, max_length=MAX_NAME_LENGTH)
    description: Union[str, Unset] = Unset()

    class Config:
        arbitrary_types_allowed = True

    @root_validator(skip_on_failure=True)
    def _any_field_set(cls, values):
        """Validate that at least one field is set."""
        values_set = {k for k, v in values.items() if not isinstance(v, Unset)}
        if not values_set:
            raise ValueError("At least one field must be set.")
        return values

# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from typing import List, Optional

from pydantic import BaseModel, Field


class PermissionResponseItemV1(BaseModel):
    """Represents a single permission entry in a response, linking a user with their role within a namespace."""

    username: str
    role: str


class PermissionsResponseV1(BaseModel):
    """Wraps a list of permission entries for a namespace, returned by the GET endpoint."""

    permissions: List[PermissionResponseItemV1]


class PermissionUpdateRequestItemV1(BaseModel):
    """Represents a single permission entry in a request, specifying a desired role for a user within a namespace."""

    username: str
    role: Optional[str] = Field(
        default=None,
        description="The role to be assigned to the user within the namespace."
        " A value of `None` indicates that the permission should be removed.",
    )


class PermissionsUpdateRequestV1(BaseModel):
    """Wraps a list of permission modification requests for a namespace, used by the PATCH endpoint."""

    permissions: List[PermissionUpdateRequestItemV1] = Field(
        description="A list of modifications to the namespace's permissions."
        " Each entry specifies a user and the role they should have or be removed from.",
    )

# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pydantic import BaseModel, Field
from pydantic import __version__ as pydantic_version


class UserResponseV1(BaseModel):
    """User info response."""

    id: int = Field(description="Internal user id, not for external usage")
    username: str = Field(description="User name, unique in the entire database")

    class Config:
        if pydantic_version >= "2":
            from_attributes = True
        else:
            orm_mode = True


class UserResponseV1WithAdmin(UserResponseV1):
    """Extended user info response including is_admin."""

    is_admin: bool = Field(description="Indicates if the user is a superadmin")

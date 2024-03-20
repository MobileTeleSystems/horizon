# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pydantic import BaseModel, Field


class UserResponseV1(BaseModel):
    """User info response."""

    id: int = Field(description="Internal user id, not for external usage")
    username: str = Field(description="User name, unique in the entire database")

    class Config:
        # pydantic v1
        orm_mode = True
        # pydantic v2
        from_attributes = True


class UserResponseV1WithAdmin(UserResponseV1):
    """Extended user info response including is_admin."""

    is_admin: bool = Field(description="Indicates if the user is a superadmin")

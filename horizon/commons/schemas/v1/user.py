# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pydantic import BaseModel


class UserResponseV1(BaseModel):
    id: int
    username: str

    class Config:
        # pydantic v1
        orm_mode = True
        # pydantic v2
        from_attributes = True

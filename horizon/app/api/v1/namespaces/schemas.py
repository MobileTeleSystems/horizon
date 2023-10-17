# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from datetime import datetime

from pydantic import BaseModel

from app.dto.unset import Unset


class ReadNamespaceSchema(BaseModel):
    id: int
    name: str
    description: str
    changed_at: datetime
    changed_by: str | None = None

    class Config:
        orm_mode = True


class CreateNamespaceSchema(BaseModel):
    name: str
    description: str = ""


class UpdateNamespaceSchema(BaseModel):
    name: str | Unset = Unset()
    description: str | Unset = Unset()

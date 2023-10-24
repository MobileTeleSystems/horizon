# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime

from pydantic import BaseModel

from horizon_commons.dto import Unset


class ReadNamespaceSchemaV1(BaseModel):
    id: int
    name: str
    description: str
    changed_at: datetime
    changed_by: str | None = None

    class Config:
        orm_mode = True


class CreateNamespaceSchemaV1(BaseModel):
    name: str
    description: str = ""


class UpdateNamespaceSchemaV1(BaseModel):
    name: str | Unset = Unset()
    description: str | Unset = Unset()

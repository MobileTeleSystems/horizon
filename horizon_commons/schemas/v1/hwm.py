# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from horizon_commons.dto import Unset


class ReadHWMSchemaV1(BaseModel):
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


class WriteHWMSchemaV1(BaseModel):
    description: str | Unset = Unset()
    type: str | Unset = Unset()
    value: Any | Unset = Unset()
    entity: str | None | Unset = Unset()
    expression: str | None | Unset = Unset()

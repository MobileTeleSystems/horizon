# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ReadHWMHistorySchemaV1(BaseModel):
    id: int
    hwm_id: int
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

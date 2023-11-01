# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import Any

from pydantic import BaseModel

from horizon_commons.schemas.v1.pagination import PaginateQueryV1


class HWMHistoryPaginateQueryV1(PaginateQueryV1):
    """Query params for HWM pagination request."""

    # more arguments can be added in future


class HWMHistoryResponseV1(BaseModel):
    """HWM history response."""

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

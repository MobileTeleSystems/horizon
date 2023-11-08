# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel

from horizon.commons.schemas.v1.pagination import PaginateQueryV1


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
    entity: Optional[str] = None
    expression: Optional[str] = None
    changed_at: datetime
    changed_by: Optional[str] = None

    class Config:
        orm_mode = True

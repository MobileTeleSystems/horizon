# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from horizon.commons.schemas.v1.pagination import PaginateQueryV1


class HWMHistoryPaginateQueryV1(PaginateQueryV1):
    """Query params for HWM pagination request."""

    # more arguments can be added in future


class HWMHistoryResponseV1(BaseModel):
    """HWM history response."""

    id: int = Field(description="Internal HWM history item id, not for external usage")
    hwm_id: int = Field(description="Internal HWM id, not for external usage")
    name: str = Field(description="HWM name, unique in the namespace")
    description: str = Field(description="HWM description")
    type: str = Field(description="HWM type, any non-empty string")
    value: Any = Field(description="HWM value, any JSON serializable value")
    entity: Optional[str] = Field(default=None, description="Name of entity associated with the HWM. Can be any string")
    expression: Optional[str] = Field(
        default=None,
        description="Expression used to calculate HWM value. Can be any string",
    )
    changed_at: datetime = Field(description="Timestamp of a change of the HWM data")
    changed_by: Optional[str] = Field(default=None, description="User who changed the HWM data")

    class Config:
        # pydantic v1
        orm_mode = True
        # pydantic v2
        from_attributes = True

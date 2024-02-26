# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from horizon.commons.schemas.v1.pagination import PaginateQueryV1


class HWMHistoryPaginateQueryV1(PaginateQueryV1):
    """Query params for HWM pagination request."""

    hwm_id: int = Field(description="HWM id")

    # more arguments can be added in future


class HWMHistoryResponseV1(BaseModel):
    """HWM history response."""

    id: int = Field(description="HWM history item id")
    hwm_id: int = Field(description="HWM id")
    namespace_id: int = Field(description="Namespace id HWM is bound to")
    name: str = Field(description="HWM name, unique in the namespace")
    description: str = Field(description="HWM description")
    type: str = Field(description="HWM type, any non-empty string")
    value: Any = Field(description="HWM value, any JSON serializable value")
    entity: Optional[str] = Field(default=None, description="Name of entity associated with the HWM. Can be any string")
    expression: Optional[str] = Field(
        default=None,
        description="Expression used to calculate HWM value. Can be any string",
    )
    action: str = Field(description="Action performed on the HWM record")
    changed_at: datetime = Field(description="Timestamp of a change of the HWM data")
    changed_by: Optional[str] = Field(default=None, description="User who changed the HWM data")

    class Config:
        # pydantic v1
        orm_mode = True
        # pydantic v2
        from_attributes = True

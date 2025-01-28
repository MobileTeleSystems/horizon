# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field
from pydantic import __version__ as pydantic_version

from horizon.commons.schemas.v1.pagination import PaginateQueryV1


class NamespaceHistoryPaginateQueryV1(PaginateQueryV1):
    """Query params for Namespace pagination request."""

    namespace_id: int = Field(description="Namespace id")

    # more arguments can be added in future


class NamespaceHistoryResponseV1(BaseModel):
    """Namespace history response."""

    id: int = Field(description="Namespace history item id")
    namespace_id: int = Field(description="Namespace id history is bound to")
    name: str = Field(description="Namespace name")
    description: str = Field(description="Namespace description")
    owned_by: Optional[str] = Field(default=None, description="The namespace owner")
    action: str = Field(description="Action performed on the namespace record")
    changed_at: datetime = Field(description="Timestamp of a change of the namespace data")
    changed_by: Optional[str] = Field(default=None, description="User who changed the namespace data")

    class Config:
        if pydantic_version >= "2":
            from_attributes = True
        else:
            orm_mode = True

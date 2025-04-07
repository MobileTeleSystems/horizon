# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field
from pydantic import __version__ as pydantic_version

if pydantic_version >= "2":
    from pydantic import BaseModel as GenericModel
else:
    from pydantic.generics import GenericModel  # type: ignore[no-redef]

from horizon.commons.dto import Pagination


class PaginateQueryV1(BaseModel):
    """Basic class with pagination query params."""

    page: int = Field(gt=0, default=1, description="Page number")
    page_size: int = Field(gt=0, le=50, default=20, description="Number of items per page")


class PageMetaResponseV1(BaseModel):
    """Page metadata response."""

    page: int = Field(description="Page number")
    page_size: int = Field(description="Number of items per page")
    total_count: int = Field(description="Total number of items")
    pages_count: int = Field(description="Number of items returned in current page")
    has_next: bool = Field(description="Is there a next page")
    has_previous: bool = Field(description="Is there a next page")
    next_page: Optional[int] = Field(description="Next page number, if any")
    previous_page: Optional[int] = Field(description="Previous page number, if any")


T = TypeVar("T", bound=BaseModel)


class PageResponseV1(GenericModel, Generic[T]):
    """Page response."""

    meta: PageMetaResponseV1 = Field(description="Page metadata")
    items: List[T] = Field(description="Page content")

    @classmethod
    def from_pagination(cls, pagination: Pagination):
        return cls(
            meta=PageMetaResponseV1(
                page=pagination.page,
                pages_count=pagination.pages_count,
                page_size=pagination.page_size,
                total_count=pagination.total_count,
                has_next=pagination.has_next,
                has_previous=pagination.has_previous,
                next_page=pagination.next_page,
                previous_page=pagination.previous_page,
            ),
            items=pagination.items,
        )

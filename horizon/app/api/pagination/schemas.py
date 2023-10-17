# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

from app.dto.pagination import Pagination


class MetaPageSchema(BaseModel):
    page: int
    pages_count: int
    total_count: int
    page_size: int
    has_next: bool
    has_previous: bool
    next_page: int | None
    previous_page: int | None


T = TypeVar("T", bound=BaseModel)


class PageSchema(GenericModel, Generic[T]):
    meta: MetaPageSchema
    items: list[T]

    @classmethod
    def from_pagination(cls, pagination: Pagination):
        return cls(
            meta=MetaPageSchema(
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

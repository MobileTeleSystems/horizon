# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from abc import ABC
from typing import Annotated, ClassVar, Generic, TypeVar

from fastapi import Depends
from sqlalchemy import ScalarResult, Select, delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql import ColumnElement
from sqlalchemy.sql.dml import ReturningDelete, ReturningInsert, ReturningUpdate

from app.db.models import Base
from app.dependencies import Stub
from app.dto.pagination import Pagination

Model = TypeVar("Model", bound=Base)


class Repository(ABC, Generic[Model]):
    MODEL_TYPE: ClassVar[type]

    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(Stub(AsyncSession))],
    ) -> None:
        self._session = session

    async def _get_by_id(
        self,
        id: int,
        *where: ColumnElement,
    ) -> Model | None:
        query: Select = select(self.MODEL_TYPE).filter_by(id=id)
        if where:
            query = query.where(*where)

        result = await self._session.scalars(query)
        return result.one()

    async def _get(self, *where: ColumnElement) -> Model | None:
        query: Select = select(self.MODEL_TYPE).where(*where)
        result = await self._session.scalars(query)
        return result.first()

    async def _create(self, data: dict) -> Model:
        insert_query: ReturningInsert[tuple[Model]] = insert(self.MODEL_TYPE).values(**data).returning(self.MODEL_TYPE)
        result = await self._session.scalars(insert_query)
        return result.one()

    async def _update(self, where: list[ColumnElement], changes: dict) -> Model | None:
        query: ReturningUpdate[tuple[Model]] = (
            update(self.MODEL_TYPE).where(*where).values(**changes).returning(self.MODEL_TYPE)
        )
        result = await self._session.scalars(query)
        return result.one()

    async def _delete(self, id: int) -> Model:
        query: ReturningUpdate[tuple[Model]] | ReturningDelete[tuple[Model]]
        if hasattr(self.MODEL_TYPE, "is_deleted"):
            query = (
                update(self.MODEL_TYPE)
                .where(self.MODEL_TYPE.id == id)  # type: ignore[attr-defined]
                .values(is_deleted=True)
                .returning(self.MODEL_TYPE)
            )
        else:
            query = (
                delete(self.MODEL_TYPE)
                .where(self.MODEL_TYPE.id == id)  # type: ignore[attr-defined]
                .returning(self.MODEL_TYPE)
            )

        result = await self._session.scalars(query)
        return result.one()

    async def _paginate(
        self,
        where: list[ColumnElement],
        order_by: list[InstrumentedAttribute],
        page: int,
        page_size: int,
    ) -> Pagination:
        query: Select = select(self.MODEL_TYPE).where(*where)
        items_result: ScalarResult[Model] = await self._session.scalars(
            query.order_by(*order_by).limit(page_size).offset((page - 1) * page_size),
        )
        total: int = await self._session.scalar(  # type: ignore[assignment]
            select(func.count()).select_from(query.subquery()),
        )
        return Pagination(
            items=items_result.all(),
            total=total,
            page=page,
            page_size=page_size,
        )

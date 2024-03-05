# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from sqlalchemy import SQLColumnExpression
from sqlalchemy.exc import IntegrityError

from horizon.backend.db.models import HWM, User
from horizon.backend.db.repositories.base import Repository
from horizon.commons.dto.pagination import Pagination
from horizon.commons.exceptions.entity import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class HWMRepository(Repository[HWM]):
    async def paginate(
        self,
        namespace_id: int,
        page: int,
        page_size: int,
        name: str | None = None,
    ) -> Pagination[HWM]:
        where: list[SQLColumnExpression] = [
            HWM.namespace_id == namespace_id,
        ]
        if name:
            where.append(HWM.name == name)

        return await self._paginate(
            where=where,
            order_by=[HWM.name],
            page=page,
            page_size=page_size,
        )

    async def count(self) -> int:
        return await self._count()

    async def get(
        self,
        hwm_id: int,
    ) -> HWM:
        result = await self._get(
            HWM.id == hwm_id,
        )
        if not result:
            raise EntityNotFoundError("HWM", "id", hwm_id)
        return result

    async def create(
        self,
        data: dict,
        user: User,
    ) -> HWM:
        try:
            result = await self._create(data={**data, "changed_by_user_id": user.id})
            await self._session.flush()
            return result
        except IntegrityError as e:
            constraint = e.__cause__.__cause__.constraint_name  # type: ignore[union-attr]

            if constraint == "fk__hwm__namespace_id__namespace":
                raise EntityNotFoundError("Namespace", "id", data["namespace_id"]) from e

            if constraint == "hwm_name_unique_per_namespace":
                raise EntityAlreadyExistsError("HWM", "name", data["name"]) from e

            raise

    async def update(
        self,
        hwm_id: int,
        changes: dict,
        user: User,
    ) -> HWM:
        try:
            result = await self._update(
                where=[HWM.id == hwm_id],
                changes={**changes, "changed_by_user_id": user.id},
            )
            if result is None:
                raise EntityNotFoundError("HWM", "id", hwm_id)

            await self._session.flush()
            await self._session.refresh(result)
            return result
        except IntegrityError as e:
            raise EntityAlreadyExistsError("HWM", "name", changes["name"]) from e

    async def delete(
        self,
        hwm_id: int,
        user: User,
    ) -> HWM:
        hwm = await self.get(hwm_id)
        await self._session.delete(hwm)
        await self._session.flush()
        return hwm

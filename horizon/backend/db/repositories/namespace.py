# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from sqlalchemy import SQLColumnExpression
from sqlalchemy.exc import IntegrityError

from horizon.backend.db.models import Namespace, User
from horizon.backend.db.repositories.base import Repository
from horizon.commons.dto import Pagination
from horizon.commons.exceptions.entity import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class NamespaceRepository(Repository[Namespace]):
    async def paginate(
        self,
        page: int,
        page_size: int,
        name: str | None = None,
    ) -> Pagination[Namespace]:
        where: list[SQLColumnExpression] = [Namespace.is_deleted.is_(False)]
        if name:
            where.append(Namespace.name == name)

        return await self._paginate(
            where=where,
            order_by=[Namespace.name],
            page=page,
            page_size=page_size,
        )

    async def count(self) -> int:
        return await self._count(where=[Namespace.is_deleted.is_(False)])

    async def get(
        self,
        namespace_id: int,
    ) -> Namespace:
        result = await self._get(
            Namespace.id == namespace_id,
            Namespace.is_deleted.is_(False),
        )
        if not result:
            raise EntityNotFoundError("Namespace", "id", namespace_id)
        return result

    async def create(
        self,
        name: str,
        description: str,
        user: User,
    ) -> Namespace:
        try:
            result = await self._create(
                data={
                    "name": name,
                    "description": description,
                    "changed_by_user_id": user.id,
                },
            )
            await self._session.flush()
            return result
        except IntegrityError as e:
            raise EntityAlreadyExistsError("Namespace", "name", name) from e

    async def update(
        self,
        namespace_id: int,
        changes: dict,
        user: User,
    ) -> Namespace:
        try:
            result = await self._update(
                where=[Namespace.id == namespace_id, Namespace.is_deleted.is_(False)],
                changes={**changes, "changed_by_user_id": user.id},
            )
            if result is None:
                raise EntityNotFoundError("Namespace", "id", namespace_id)

            await self._session.flush()
            return result
        except IntegrityError as e:
            raise EntityAlreadyExistsError(
                "Namespace",
                "name",
                changes.get("name"),
            ) from e

    async def delete(
        self,
        namespace_id: int,
        user: User,
    ) -> None:
        result = await self._update(
            where=[Namespace.id == namespace_id, Namespace.is_deleted.is_(False)],
            changes={"is_deleted": True, "changed_by_user_id": user.id},
        )
        if result is None:
            raise EntityNotFoundError("Namespace", "id", namespace_id)

        await self._session.flush()

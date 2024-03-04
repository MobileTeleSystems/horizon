# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy import SQLColumnExpression, select
from sqlalchemy.exc import IntegrityError

from horizon.backend.db.models import Namespace, NamespaceUser, NamespaceUserRole, User
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
        where: list[SQLColumnExpression] = [Namespace.name == name] if name else []

        return await self._paginate(
            where=where,
            order_by=[Namespace.name],
            page=page,
            page_size=page_size,
        )

    async def count(self) -> int:
        return await self._count()

    async def get(
        self,
        namespace_id: int,
    ) -> Namespace:
        result = await self._get(
            Namespace.id == namespace_id,
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
                    "owner_id": user.id,
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
                where=[Namespace.id == namespace_id],
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
    ) -> Namespace:
        namespace = await self.get(namespace_id)
        await self._session.delete(namespace)
        await self._session.flush()
        return namespace

    async def check_user_permission(self, user: User, namespace_id: int, required_role: NamespaceUserRole) -> None:
        owner_check = await self._session.execute(select(Namespace.owner_id).where(Namespace.id == namespace_id))
        owner_id = owner_check.scalar_one_or_none()
        if owner_id is None:
            raise EntityNotFoundError("Namespace", "owner_id", owner_id)

        if owner_id == user.id:
            user_role = NamespaceUserRole.owner
        else:
            role_result = await self._session.execute(
                select(NamespaceUser.role).where(
                    NamespaceUser.namespace_id == namespace_id,
                    NamespaceUser.user_id == user.id,
                ),
            )
            user_role_value = role_result.scalars().first()
            user_role = NamespaceUserRole[user_role_value] if user_role_value else NamespaceUserRole.authorized

        if user_role < required_role:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Action not allowed")

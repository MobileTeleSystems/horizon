# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from sqlalchemy import SQLColumnExpression, delete, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError

from horizon.backend.db.models import Namespace, NamespaceUser, User
from horizon.backend.db.repositories.base import Repository
from horizon.commons.dto import Pagination, Role
from horizon.commons.exceptions import EntityAlreadyExistsError, EntityNotFoundError


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
            await self._session.refresh(result)
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
    ) -> Namespace:
        result = await self.get(namespace_id)
        await self._session.delete(result)
        await self._session.flush()
        return result

    async def get_user_role(self, user_id: int, namespace_id: int) -> Role | None:
        owner_result = await self._session.execute(
            select(Namespace.owner_id).where(
                Namespace.id == namespace_id,
                Namespace.owner_id == user_id,
            ),
        )
        owner_id = owner_result.scalar_one_or_none()
        if owner_id:
            return Role.OWNER

        role_result = await self._session.execute(
            select(NamespaceUser.role).where(
                NamespaceUser.namespace_id == namespace_id,
                NamespaceUser.user_id == user_id,
            ),
        )
        user_role = role_result.scalar_one_or_none()
        if user_role:
            return user_role

        return None

    async def get_all_roles(self, namespace_id: int) -> dict[User, Role]:
        roles_dict = {}

        namespace = await self.get(namespace_id)
        owner = await self._session.get(User, namespace.owner_id)
        if owner:
            roles_dict[owner] = Role.OWNER

        query = (
            select(User, NamespaceUser.role)
            .join(NamespaceUser, User.id == NamespaceUser.user_id)
            .where(NamespaceUser.namespace_id == namespace_id)
        )
        result = await self._session.execute(query)
        for user, role in result.fetchall():
            roles_dict[user] = Role[role]

        return roles_dict

    async def set_role(self, namespace_id: int, user_id: int, role: Role) -> None:
        # create an "upsert" statement using PostgreSQL's ON CONFLICT syntax.
        stmt = pg_insert(NamespaceUser).values(namespace_id=namespace_id, user_id=user_id, role=role.name)
        stmt = stmt.on_conflict_do_update(
            index_elements=[NamespaceUser.namespace_id, NamespaceUser.user_id],
            set_={"role": role},
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def delete_role(self, namespace_id: int, user_id: int) -> None:
        await self._session.execute(
            delete(NamespaceUser).where(NamespaceUser.namespace_id == namespace_id, NamespaceUser.user_id == user_id),
        )
        await self._session.flush()

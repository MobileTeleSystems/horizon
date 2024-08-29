# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Dict, cast

from sqlalchemy import SQLColumnExpression, delete, select, update
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError

from horizon.backend.db.models import (
    Namespace,
    NamespaceUser,
    NamespaceUserRoleInt,
    User,
)
from horizon.backend.db.repositories.base import Repository
from horizon.commons.dto import Pagination
from horizon.commons.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    PermissionDeniedError,
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

    async def check_user_permission(self, user_id: int, namespace_id: int, required_role: NamespaceUserRoleInt) -> None:

        # if the user is a SUPERADMIN, they inherently have all permissions
        superadmin_user = await self._session.execute(select(User.is_admin).where(User.id == user_id))
        if superadmin_user.scalar_one_or_none():
            return

        owner_check = await self._session.execute(select(Namespace.owner_id).where(Namespace.id == namespace_id))
        owner_id = owner_check.scalar_one_or_none()
        if owner_id is None:
            raise EntityNotFoundError("Namespace", "id", namespace_id)

        if owner_id == user_id:
            user_role = NamespaceUserRoleInt.OWNER
        else:
            role_result = await self._session.execute(
                select(NamespaceUser.role).where(
                    NamespaceUser.namespace_id == namespace_id,
                    NamespaceUser.user_id == user_id,
                ),
            )
            user_role_value = role_result.scalars().first()
            user_role = NamespaceUserRoleInt[user_role_value] if user_role_value else NamespaceUserRoleInt.GUEST

        if user_role < required_role:
            raise PermissionDeniedError(required_role.name, user_role.name)

    async def get_namespace_users_permissions(self, namespace_id: int) -> Dict[User, NamespaceUserRoleInt]:
        permissions_dict = {}

        namespace = await self.get(namespace_id)
        owner = await self._session.get(User, namespace.owner_id)
        owner = cast(User, owner)
        permissions_dict[owner] = NamespaceUserRoleInt.OWNER

        query = (
            select(User, NamespaceUser.role)
            .join(NamespaceUser, User.id == NamespaceUser.user_id)
            .where(NamespaceUser.namespace_id == namespace_id)
            .order_by(NamespaceUser.role.desc(), User.username)
        )
        result = await self._session.execute(query)
        for user, role in result.fetchall():
            permissions_dict[user] = NamespaceUserRoleInt[role]

        return permissions_dict

    async def set_new_owner(self, namespace_id: int, new_owner_id: int) -> None:
        await self._session.execute(update(Namespace).where(Namespace.id == namespace_id).values(owner_id=new_owner_id))
        await self._session.execute(
            delete(NamespaceUser).where(
                NamespaceUser.namespace_id == namespace_id,
                NamespaceUser.user_id == new_owner_id,
            ),
        )

    async def update_permission(self, namespace_id: int, user_id: int, role: NamespaceUserRoleInt) -> None:
        # create an "upsert" statement using PostgreSQL's ON CONFLICT syntax.
        stmt = pg_insert(NamespaceUser).values(namespace_id=namespace_id, user_id=user_id, role=role.name)
        stmt = stmt.on_conflict_do_update(
            index_elements=[NamespaceUser.namespace_id, NamespaceUser.user_id],
            set_={"role": role.name},
        )
        await self._session.execute(stmt)

    async def delete_permission(self, namespace_id: int, user_id: int) -> None:
        await self._session.execute(
            delete(NamespaceUser).where(NamespaceUser.namespace_id == namespace_id, NamespaceUser.user_id == user_id),
        )

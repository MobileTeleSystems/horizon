# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Dict, Set

from sqlalchemy import SQLColumnExpression, delete, insert, select, update
from sqlalchemy.exc import IntegrityError

from horizon.backend.db.models import Namespace, NamespaceUser, NamespaceUserRole, User
from horizon.backend.db.repositories.base import Repository
from horizon.commons.dto import Pagination
from horizon.commons.exceptions import (
    BadRequestError,
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

    async def check_user_permission(self, user_id: int, namespace_id: int, required_role: NamespaceUserRole) -> None:
        owner_check = await self._session.execute(select(Namespace.owner_id).where(Namespace.id == namespace_id))
        owner_id = owner_check.scalar_one_or_none()
        if owner_id is None:
            raise EntityNotFoundError("Namespace", "id", namespace_id)

        if owner_id == user_id:
            user_role = NamespaceUserRole.OWNER
        else:
            role_result = await self._session.execute(
                select(NamespaceUser.role).where(
                    NamespaceUser.namespace_id == namespace_id,
                    NamespaceUser.user_id == user_id,
                ),
            )
            user_role_value = role_result.scalars().first()
            user_role = NamespaceUserRole[user_role_value] if user_role_value else NamespaceUserRole.GUEST

        if user_role < required_role:
            raise PermissionDeniedError(required_role.name, user_role.name)

    async def get_namespace_users_permissions(self, namespace_id: int) -> Dict[User, NamespaceUserRole]:
        permissions_dict = {}

        namespace = await self.get(namespace_id)
        if namespace.owner_id is not None:
            owner = await self._session.get(User, namespace.owner_id)
            permissions_dict[owner] = NamespaceUserRole.OWNER

        query = (
            select(User, NamespaceUser.role)
            .join(NamespaceUser, User.id == NamespaceUser.user_id)
            .where(NamespaceUser.namespace_id == namespace_id)
        )
        result = await self._session.execute(query)
        for user, role in result.fetchall():
            permissions_dict[user] = NamespaceUserRole[role]

        return permissions_dict  # type: ignore[return-value]

    async def update_user_permission(  # noqa: WPS217
        self,
        namespace_id: int,
        user_id: int,
        role: NamespaceUserRole,
        seen_user_ids: Set[int],
        owner_changed: dict,
    ) -> None:
        if user_id in seen_user_ids:
            raise BadRequestError("Duplicate username detected. Each username must appear only once.")

        if role == NamespaceUserRole.OWNER:
            if owner_changed["changed"]:
                raise BadRequestError("Multiple owner role assignments detected. Only one owner can be assigned.")

            await self._session.execute(
                update(Namespace).where(Namespace.id == namespace_id).values(owner_id=user_id),
            )
            owner_changed["changed"] = True

            await self._session.execute(
                delete(NamespaceUser).where(
                    NamespaceUser.namespace_id == namespace_id,
                    NamespaceUser.user_id == user_id,
                ),
            )
            return

        namespace = await self.get(namespace_id=namespace_id)
        if namespace.owner_id == user_id and role != NamespaceUserRole.OWNER:
            # raise an error if the current owner tries to change their role to something other than OWNER
            # without reassigning new OWNER to namespace
            raise BadRequestError(
                "Operation forbidden: The current owner cannot change their rights"
                " without reassigning them to another user.",
            )

        existing_permission_result = await self._session.execute(
            select(NamespaceUser).where(NamespaceUser.namespace_id == namespace_id, NamespaceUser.user_id == user_id),
        )
        existing_permission = existing_permission_result.scalars().first()

        if existing_permission:
            await self._session.execute(
                update(NamespaceUser)
                .where(NamespaceUser.namespace_id == namespace_id, NamespaceUser.user_id == user_id)
                .values(role=role.name),
            )
        else:
            await self._session.execute(
                insert(NamespaceUser).values(namespace_id=namespace_id, user_id=user_id, role=role.name),
            )
        seen_user_ids.add(user_id)

    async def delete_permission(self, namespace_id: int, user_id: int) -> None:
        await self._session.execute(
            delete(NamespaceUser).where(
                NamespaceUser.namespace_id == namespace_id,
                NamespaceUser.user_id == user_id,
            ),
        )

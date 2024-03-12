# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import List

from fastapi import HTTPException, status
from sqlalchemy import SQLColumnExpression, delete, insert, select, update
from sqlalchemy.exc import IntegrityError

from horizon.backend.db.models import Namespace, NamespaceUser, NamespaceUserRole, User
from horizon.backend.db.repositories.base import Repository
from horizon.commons.dto import Pagination
from horizon.commons.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    PermissionDeniedError,
)
from horizon.commons.schemas.v1 import PermissionsUpdateRequestV1


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

    async def get_permissions(self, namespace_id: int) -> List[dict]:
        namespace = await self.get(namespace_id)

        query = (
            select(User.username, NamespaceUser.role)
            .join(NamespaceUser, User.id == NamespaceUser.user_id)
            .where(NamespaceUser.namespace_id == namespace_id)
        )

        result = await self._session.execute(query)
        permissions = [{"username": namespace.owned_by, "role": NamespaceUserRole.OWNER.name}]
        for user_name, role in result.fetchall():
            permissions.append({"username": user_name, "role": role})

        return permissions

    async def update_permissions(  # noqa:  WPS217
        self,
        namespace_id: int,
        owner_id: int,
        permissions_update: PermissionsUpdateRequestV1,
    ) -> List[dict]:
        updated_permissions = []
        new_owner_id = None
        seen_usernames = set()
        owner_assignment_count = 0

        # sort permissions so that "OWNER" role updates come first to not depend on order of assignments
        sorted_permissions = sorted(
            permissions_update.permissions,
            key=lambda perm: perm.role.upper() == NamespaceUserRole.OWNER.name if perm.role else False,
            reverse=True,
        )

        for permission in sorted_permissions:
            # TODO: create custom exception if logic is acceptable
            if permission.username in seen_usernames:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Duplicate username detected: {permission.username}. Each username must appear only once.",
                )
            user = await self._get_user_by_username(permission.username)

            user_id = user.id

            if user_id == owner_id:
                role_enum = NamespaceUserRole[permission.role.upper()] if permission.role else None
                if role_enum != NamespaceUserRole.OWNER and not new_owner_id:
                    # raise an error if the current owner tries to change their role to something other than OWNER
                    # without reassigning new OWNER to namespace
                    # TODO: create custom exception if logic is acceptable
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Operation forbidden: The current owner cannot change their rights"
                        " without reassigning them to another user.",
                    )

            if permission.role is None:
                await self._session.execute(
                    delete(NamespaceUser).where(
                        NamespaceUser.namespace_id == namespace_id,
                        NamespaceUser.user_id == user_id,
                    ),
                )
            else:
                role_enum = NamespaceUserRole[permission.role.upper()]
                if role_enum == NamespaceUserRole.OWNER:
                    owner_assignment_count += 1
                    if owner_assignment_count > 1:
                        # TODO: create custom exception if logic is acceptable
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Multiple owner role assignments detected. Only one owner can be assigned.",
                        )
                    new_owner_id = user_id
                    await self._session.execute(
                        update(Namespace).where(Namespace.id == namespace_id).values(owner_id=user_id),
                    )
                    await self._session.execute(
                        delete(NamespaceUser).where(
                            NamespaceUser.namespace_id == namespace_id,
                            NamespaceUser.user_id == user_id,
                        ),
                    )
                else:
                    result = await self._session.execute(
                        select(NamespaceUser).where(
                            NamespaceUser.namespace_id == namespace_id,
                            NamespaceUser.user_id == user_id,
                        ),
                    )
                    existing_record = result.scalars().first()
                    if existing_record:
                        await self._session.execute(
                            update(NamespaceUser)
                            .where(NamespaceUser.namespace_id == namespace_id, NamespaceUser.user_id == user_id)
                            .values(role=role_enum.name),
                        )
                    else:
                        await self._session.execute(
                            insert(NamespaceUser).values(
                                namespace_id=namespace_id,
                                user_id=user_id,
                                role=role_enum.name,
                            ),
                        )

                updated_permissions.append({"username": permission.username, "role": role_enum.name})
                seen_usernames.add(permission.username)

        return updated_permissions

    async def _get_user_by_username(self, username: str) -> User:
        query = select(User).where(User.username == username)
        result = await self._session.execute(query)
        user = result.scalars().first()
        if not user:
            raise EntityNotFoundError("User", "username", username)
        return user

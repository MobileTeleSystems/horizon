# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import SQLColumnExpression, select
from sqlalchemy.exc import IntegrityError

from horizon.backend.db.models import (
    HWM,
    Namespace,
    NamespaceUser,
    NamespaceUserRole,
    User,
)
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

    async def check_user_permission(
        self,
        user: User,
        required_role: NamespaceUserRole,
        hwm_id: Optional[int] = None,
        namespace_id: Optional[int] = None,
    ) -> None:
        if hwm_id:
            hwm_query_result = await self._session.execute(select(HWM.namespace_id).where(HWM.id == hwm_id))
            namespace_id_from_hwm = hwm_query_result.scalar_one_or_none()
            if namespace_id_from_hwm is None:
                raise EntityNotFoundError("HWM", "id", hwm_id)
            namespace_id = namespace_id_from_hwm

        owner_check = await self._session.execute(select(Namespace.owner_id).where(Namespace.id == namespace_id))
        owner_id = owner_check.scalar_one_or_none()
        user_role = NamespaceUserRole.owner if owner_id == user.id else NamespaceUserRole.authorized

        if owner_id is None:
            raise EntityNotFoundError("Namespace", "owner_id", owner_id)

        if owner_id != user.id:
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

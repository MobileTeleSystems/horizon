# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

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
    ) -> Pagination[Namespace]:
        return await self._paginate(
            where=[Namespace.is_deleted.is_(False)],
            order_by=[Namespace.name],
            page=page,
            page_size=page_size,
        )

    async def get_by_name(self, name: str) -> Namespace:
        result = await self._get(
            Namespace.name == name,
            Namespace.is_deleted.is_(False),
        )
        if result is None:
            raise EntityNotFoundError("Namespace", "name", name)
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
        name: str,
        changes: dict,
        user: User,
    ) -> Namespace:
        try:
            result = await self._update(
                where=[Namespace.name == name, Namespace.is_deleted.is_(False)],
                changes={**changes, "changed_by_user_id": user.id},
            )
            if result is None:
                raise EntityNotFoundError("Namespace", "name", name)

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
        name: str,
        user: User,
    ) -> None:
        result = await self._update(
            where=[Namespace.name == name, Namespace.is_deleted.is_(False)],
            changes={"is_deleted": True, "changed_by_user_id": user.id},
        )
        if result is None:
            raise EntityNotFoundError("Namespace", "name", name)

        await self._session.flush()
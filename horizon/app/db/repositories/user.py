# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from typing import ClassVar

from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.db.repositories.base import Repository
from app.dto.pagination import Pagination
from app.exceptions.entity import EntityAlreadyExistsError, EntityNotFoundError


class UserRepository(Repository[User]):
    MODEL_TYPE: ClassVar[type] = User

    async def paginate(
        self,
        page: int,
        page_size: int,
    ) -> Pagination:
        return await self._paginate(
            where=[User.is_active.is_(True), User.is_deleted.is_(False)],
            order_by=[User.username],
            page=page,
            page_size=page_size,
        )

    async def get_by_id(self, id: int) -> User:
        result = await self._get_by_id(id, User.is_deleted.is_(False))
        if result is None:
            raise EntityNotFoundError(User, "id", id)
        return result

    async def get_by_username(self, username: str) -> User:
        result = await self._get(
            User.username == username,
            User.is_active.is_(True),
            User.is_deleted.is_(False),
        )
        if result is None:
            raise EntityNotFoundError(User, "username", username)
        return result

    async def create(
        self,
        username: str,
    ) -> User:
        try:
            result = await self._create(data={"username": username})
            await self._session.flush()
            return result
        except IntegrityError as e:
            raise EntityAlreadyExistsError(User, "username", username) from e

    async def get_or_create(
        self,
        username: str,
    ) -> User:
        result = await self._get(User.username == username)
        if result is None:
            result = await self.create(username=username)
        elif result.is_deleted:
            raise EntityNotFoundError(User, "username", username)
        return result

    async def update(self, user_id: int, changes: dict) -> User:
        try:
            result = await self._update(
                where=[User.id == user_id, User.is_deleted.is_(False)],
                changes=changes,
            )
            if result is None:
                raise EntityNotFoundError(User, "id", id)

            await self._session.flush()
            return result
        except IntegrityError as e:
            raise EntityAlreadyExistsError(
                User,
                "username",
                changes.get("username"),
            ) from e

# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy.exc import IntegrityError

from horizon.backend.db.models import User
from horizon.backend.db.repositories.base import Repository
from horizon.commons.exceptions.entity import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class UserRepository(Repository[User]):
    async def count(self) -> int:
        return await self._count(where=[User.is_active.is_(True)])

    async def get_by_id(self, user_id: int) -> User:
        result = await self._get_by_id(user_id)
        if result is None:
            raise EntityNotFoundError("User", "id", user_id)
        return result

    async def get_by_username(self, username: str) -> User:
        user = await self._get(User.username == username)
        if not user:
            raise EntityNotFoundError("User", "username", username)
        return user

    async def create(
        self,
        username: str,
    ) -> User:
        try:
            result = await self._create(data={"username": username})
            await self._session.flush()
            return result
        except IntegrityError as e:
            raise EntityAlreadyExistsError("User", "username", username) from e

    async def get_or_create(
        self,
        username: str,
    ) -> User:
        result = await self._get(User.username == username)
        if not result:
            result = await self.create(username)
        return result

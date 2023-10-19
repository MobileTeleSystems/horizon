# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.db.repositories.base import Repository
from app.exceptions.entity import EntityAlreadyExistsError, EntityNotFoundError


class UserRepository(Repository[User]):
    async def get_by_id(self, user_id: int) -> User:
        result = await self._get_by_id(user_id, User.is_deleted.is_(False))
        if result is None:
            raise EntityNotFoundError(User, "id", user_id)
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

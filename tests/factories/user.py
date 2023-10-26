# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from polyfactory import Ignore
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.db.models.user import User


class UserFactory(SQLAlchemyFactory[User]):
    __model__ = User

    is_active = True
    is_deleted = False
    created_at = Ignore()
    updated_at = Ignore()


@pytest_asyncio.fixture(params=[{}])
async def new_user(request: pytest.FixtureRequest, async_session: AsyncSession) -> AsyncGenerator[User, None]:
    params = request.param
    user = UserFactory.build(**params)

    yield user

    query = delete(User).where(User.username == user.username)
    await async_session.execute(query)
    await async_session.commit()


@pytest_asyncio.fixture(params=[{}])
async def user(request: pytest.FixtureRequest, async_session: AsyncSession) -> AsyncGenerator[User, None]:
    UserFactory.__async_session__ = async_session
    params = request.param
    user = await UserFactory.create_async(**params)
    # this is not required for backend tests, but needed by client tests
    await async_session.commit()

    # remove current object from async_session. this is required to compare object against new state fetched
    # from database, and also to remove it from cache
    user_id = user.id
    async_session.expunge(user)
    yield user

    query = delete(User).where(User.id == user_id)
    await async_session.execute(query)
    await async_session.commit()

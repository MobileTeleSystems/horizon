# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections.abc import AsyncGenerator
from random import randint

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.backend.db.models import User
from tests.factories.base import random_datetime, random_string


def user_factory(**kwargs):
    data = {
        "id": randint(0, 10000000),
        "username": random_string(),
        "created_at": random_datetime(),
        "updated_at": random_datetime(),
        "is_active": True,
        "is_deleted": False,
    }
    data.update(kwargs)
    return User(**data)


@pytest_asyncio.fixture(params=[{}])
async def new_user(request: pytest.FixtureRequest, async_session: AsyncSession) -> AsyncGenerator[User, None]:
    params = request.param
    user = user_factory(**params)
    yield user

    query = delete(User).where(User.username == user.username)
    await async_session.execute(query)
    await async_session.commit()


@pytest_asyncio.fixture(params=[{}])
async def user(request: pytest.FixtureRequest, async_session: AsyncSession) -> AsyncGenerator[User, None]:
    params = request.param
    user = user_factory(**params)
    async_session.add(user)
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


@pytest_asyncio.fixture(params=[(5, {})])
async def users(
    request: pytest.FixtureRequest,
    async_session: AsyncSession,
) -> AsyncGenerator[list[User], None]:
    size, params = request.param
    result = [user_factory(**params) for _ in range(size)]
    for item in result:
        async_session.add(item)

    # this is not required for backend tests, but needed by client tests
    await async_session.commit()

    user_ids = []
    for item in result:
        user_ids.append(item.id)
        async_session.expunge(item)

    yield result

    query = delete(User).where(User.id.in_(user_ids))
    await async_session.execute(query)
    await async_session.commit()

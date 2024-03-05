# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import secrets
from collections.abc import AsyncGenerator
from random import randint
from typing import AsyncContextManager, Callable

import pytest
import pytest_asyncio
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.backend.db.models import Namespace, NamespaceUser, NamespaceUserRole, User
from tests.factories.base import random_string


def user_factory(**kwargs):
    data = {
        "id": randint(0, 10000000),
        "username": random_string(),
        "is_active": True,
    }
    data.update(kwargs)
    return User(**data)


@pytest_asyncio.fixture(params=[{}])
async def new_user(
    request: pytest.FixtureRequest,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[User, None]:
    params = request.param
    user = user_factory(**params)
    yield user

    query = delete(User).where(User.username == user.username)

    # do not use the same session in tests and fixture teardown
    # see https://github.com/MobileTeleSystems/horizon/pull/6
    async with async_session_factory() as async_session:
        await async_session.execute(query)
        await async_session.commit()


@pytest_asyncio.fixture(params=[{}])
async def user(
    request: pytest.FixtureRequest,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[User, None]:
    params = request.param
    user = user_factory(**params)
    del user.id
    async with async_session_factory() as async_session:
        async_session.add(user)
        # this is not required for backend tests, but needed by client tests
        await async_session.commit()

        # remove current object from async_session. this is required to compare object against new state fetched
        # from database, and also to remove it from cache
        user_id = user.id
        async_session.expunge(user)

    yield user

    namespace_query = delete(Namespace).where(Namespace.owner_id == user_id)
    user_query = delete(User).where(User.id == user_id)
    async with async_session_factory() as async_session:
        await async_session.execute(namespace_query)
        await async_session.execute(user_query)
        await async_session.commit()


@pytest_asyncio.fixture(params=[(5, {})])
async def users(
    request: pytest.FixtureRequest,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[list[User], None]:
    size, params = request.param
    result = [user_factory(**params) for _ in range(size)]
    async with async_session_factory() as async_session:
        for item in result:
            del item.id
            async_session.add(item)

        # this is not required for backend tests, but needed by client tests
        await async_session.commit()

        user_ids = []
        for item in result:
            user_ids.append(item.id)
            async_session.expunge(item)

    yield result

    query = delete(User).where(User.id.in_(user_ids))
    async with async_session_factory() as async_session:
        await async_session.execute(query)
        await async_session.commit()


@pytest_asyncio.fixture
async def user_with_role(
    request: pytest.FixtureRequest,
    user: User,
    namespace: Namespace,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[tuple[User, Namespace], None]:
    role_tuple = request.param
    role = role_tuple[0]
    fake_owner = None

    if role != NamespaceUserRole.OWNER:
        async with async_session_factory() as async_session:
            fake_owner = User(
                username=secrets.token_hex(5),
                is_active=True,
            )
            async_session.add(fake_owner)
            await async_session.commit()

            namespace.owner_id = fake_owner.id
            async_session.add(namespace)

            namespace_user = NamespaceUser(namespace_id=namespace.id, user_id=user.id, role=role.name)
            async_session.add(namespace_user)
            await async_session.commit()

    yield user, namespace

    async with async_session_factory() as async_session:
        if fake_owner:
            await async_session.execute(
                update(Namespace).where(Namespace.owner_id == fake_owner.id).values(owner_id=user.id)
            )

            await async_session.execute(delete(NamespaceUser).where(NamespaceUser.namespace_id == namespace.id))

            await async_session.execute(delete(User).where(User.id == fake_owner.id))

        await async_session.commit()

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections.abc import AsyncGenerator
from random import randint

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.backend.db.models import Namespace, User
from tests.factories.base import random_datetime, random_string


def namespace_factory(**kwargs):
    data = {
        "id": randint(0, 10000000),
        "name": random_string(),
        "description": random_string(),
        "changed_at": random_datetime(),
        "is_deleted": False,
    }
    data.update(kwargs)
    return Namespace(**data)


@pytest_asyncio.fixture(params=[{}])
async def new_namespace(request: pytest.FixtureRequest, async_session: AsyncSession) -> AsyncGenerator[Namespace, None]:
    params = request.param
    namespace = namespace_factory(**params)
    yield namespace

    query = delete(Namespace).where(Namespace.name == namespace.name)
    await async_session.execute(query)
    await async_session.commit()


@pytest_asyncio.fixture(params=[{}])
async def namespace(
    user: User,
    request: pytest.FixtureRequest,
    async_session: AsyncSession,
) -> AsyncGenerator[Namespace, None]:
    params = request.param
    namespace = namespace_factory(**params, changed_by_user_id=user.id)
    del namespace.id
    async_session.add(namespace)
    # this is not required for backend tests, but needed by client tests
    await async_session.commit()

    # remove current object from async_session. this is required to compare object against new state fetched
    # from database, and also to remove it from cache
    namespace_id = namespace.id
    await async_session.refresh(namespace, attribute_names=["changed_by_user"])
    async_session.expunge(namespace)
    yield namespace

    query = delete(Namespace).where(Namespace.id == namespace_id)
    await async_session.execute(query)
    await async_session.commit()


@pytest_asyncio.fixture(params=[(5, {})])
async def namespaces(
    user: User,
    request: pytest.FixtureRequest,
    async_session: AsyncSession,
) -> AsyncGenerator[list[Namespace], None]:
    size, params = request.param
    result = [namespace_factory(changed_by_user_id=user.id, **params) for _ in range(size)]
    for item in result:
        del item.id
        async_session.add(item)

    # this is not required for backend tests, but needed by client tests
    await async_session.commit()

    namespace_ids = []
    for item in result:
        namespace_ids.append(item.id)
        # before removing object from Session load all relationships
        await async_session.refresh(item, attribute_names=["changed_by_user"])
        async_session.expunge(item)

    yield result

    query = delete(Namespace).where(Namespace.id.in_(namespace_ids))
    await async_session.execute(query)
    await async_session.commit()

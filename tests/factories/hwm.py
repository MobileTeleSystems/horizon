# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from random import randint
from typing import AsyncContextManager, Callable

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.backend.db.models import HWM, Namespace, User
from tests.factories.base import random_string


def hwm_factory(**kwargs):
    data = {
        "id": randint(0, 10000000),
        "name": random_string(),
        "description": random_string(),
        "value": random_string(),
        "type": random_string(),
        "entity": random_string(),
        "expression": random_string(),
        "changed_at": datetime.now(timezone.utc),
    }
    data.update(kwargs)
    return HWM(**data)


@pytest_asyncio.fixture(params=[{}])
async def new_hwm(
    request: pytest.FixtureRequest,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[HWM, None]:
    params = request.param
    item = hwm_factory(**params)
    yield item

    query = delete(HWM).where(HWM.name == item.name, HWM.namespace_id == item.namespace_id)

    # do not use the same session in tests and fixture teardown
    # see https://github.com/MobileTeleSystems/horizon/pull/6
    async with async_session_factory() as async_session:
        await async_session.execute(query)
        await async_session.commit()


@pytest_asyncio.fixture(params=[{}])
async def hwm(
    user: User,
    namespace: Namespace,
    request: pytest.FixtureRequest,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[HWM, None]:
    params = request.param
    item = hwm_factory(namespace_id=namespace.id, changed_by_user_id=user.id, **params)
    del item.id
    async with async_session_factory() as async_session:
        async_session.add(item)
        # this is not required for backend tests, but needed by client tests
        await async_session.commit()

        # remove current object from async_session. this is required to compare object against new state fetched
        # from database, and also to remove it from cache
        hwm_id = item.id
        await async_session.refresh(item, attribute_names=["changed_by_user", "namespace"])
        async_session.expunge(item)

    yield item

    query = delete(HWM).where(HWM.id == hwm_id)
    async with async_session_factory() as async_session:
        await async_session.execute(query)
        await async_session.commit()


@pytest_asyncio.fixture(params=[(5, {})])
async def hwms(
    user: User,
    namespace: Namespace,
    request: pytest.FixtureRequest,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[list[HWM], None]:
    size, params = request.param
    result = [hwm_factory(namespace_id=namespace.id, changed_by_user_id=user.id, **params) for _ in range(size)]
    async with async_session_factory() as async_session:
        for item in result:
            del item.id
            async_session.add(item)

        # this is not required for backend tests, but needed by client tests
        await async_session.commit()

        hwm_ids = []
        for item in result:
            hwm_ids.append(item.id)
            # before removing object from Session load all relationships
            await async_session.refresh(item, attribute_names=["changed_by_user", "namespace"])
            async_session.expunge(item)

    yield result

    query = delete(HWM).where(HWM.id.in_(hwm_ids))
    async with async_session_factory() as async_session:
        await async_session.execute(query)
        await async_session.commit()

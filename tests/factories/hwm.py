# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.db.models import HWM, Namespace, User
from tests.factories.base import random_datetime, random_string


def hwm_factory(**kwargs):
    data = {
        "name": random_string(),
        "description": random_string(),
        "value": random_string(),
        "type": random_string(),
        "entity": random_string(),
        "expression": random_string(),
        "changed_at": random_datetime(),
        "is_deleted": False,
    }
    data.update(kwargs)
    return HWM(**data)


@pytest_asyncio.fixture(params=[{}])
async def new_hwm(request: pytest.FixtureRequest, async_session: AsyncSession) -> AsyncGenerator[HWM, None]:
    params = request.param
    hwm = hwm_factory(**params)
    yield hwm

    query = delete(HWM).where(HWM.name == hwm.name)
    await async_session.execute(query)
    await async_session.commit()


@pytest_asyncio.fixture(params=[{}])
async def hwm(
    user: User,
    namespace: Namespace,
    request: pytest.FixtureRequest,
    async_session: AsyncSession,
) -> AsyncGenerator[HWM, None]:
    params = request.param
    hwm = hwm_factory(namespace_id=namespace.id, changed_by_user_id=user.id, **params)
    async_session.add(hwm)
    # this is not required for backend tests, but needed by client tests
    await async_session.commit()

    # remove current object from async_session. this is required to compare object against new state fetched
    # from database, and also to remove it from cache
    hwm_id = hwm.id
    await async_session.refresh(hwm, attribute_names=["changed_by_user", "namespace"])
    async_session.expunge(hwm)
    yield hwm

    query = delete(HWM).where(HWM.id == hwm_id)
    await async_session.execute(query)
    await async_session.commit()


@pytest_asyncio.fixture(params=[(5, {})])
async def hwms(
    user: User,
    namespace: Namespace,
    request: pytest.FixtureRequest,
    async_session: AsyncSession,
) -> AsyncGenerator[list[HWM], None]:
    size, params = request.param
    result = [hwm_factory(namespace_id=namespace.id, changed_by_user_id=user.id, **params) for _ in range(size)]
    for item in result:
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
    await async_session.execute(query)
    await async_session.commit()

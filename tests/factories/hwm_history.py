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

from horizon.backend.db.models import HWM, HWMHistory, Namespace, User
from tests.factories.base import random_string


def hwm_history_factory(**kwargs):
    data = {
        "id": randint(0, 10000000),
        "name": random_string(),
        "description": random_string(),
        "value": random_string(),
        "type": random_string(),
        "entity": random_string(),
        "expression": random_string(),
        "changed_at": datetime.now(timezone.utc),
        "action": "Created",
    }
    data.update(kwargs)
    return HWMHistory(**data)


@pytest_asyncio.fixture(params=[(5, {})])
async def hwm_history_items(
    user: User,
    namespace: Namespace,
    hwm: HWM,
    request: pytest.FixtureRequest,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[list[HWMHistory], None]:
    size, params = request.param
    result = [
        hwm_history_factory(namespace_id=namespace.id, hwm_id=hwm.id, changed_by_user_id=user.id, **params)
        for _ in range(size)
    ]

    # do not use the same session in tests and fixture teardown
    # see https://github.com/MobileTeleSystems/horizon/pull/6
    async with async_session_factory() as async_session:
        for item in result:
            del item.id
            async_session.add(item)

        # this is not required for backend tests, but needed by client tests
        await async_session.commit()

        for item in result:
            # before removing object from Session load all relationships
            await async_session.refresh(item, attribute_names=["changed_by_user"])
            async_session.expunge(item)

    yield result

    query = delete(HWMHistory).where(HWMHistory.hwm_id == hwm.id)
    async with async_session_factory() as async_session:
        await async_session.execute(query)
        await async_session.commit()


@pytest_asyncio.fixture(params=[(5, {})])
async def hwm_history_items_for_hwms(
    user: User,
    namespace: Namespace,
    hwms: list[HWM],
    request: pytest.FixtureRequest,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[list[HWMHistory], None]:
    size, params = request.param
    hwm_history_records = []

    async with async_session_factory() as async_session:
        for hwm in hwms:
            for _ in range(size):
                hwm_history_record = hwm_history_factory(
                    namespace_id=namespace.id, hwm_id=hwm.id, changed_by_user_id=user.id, **params
                )
                async_session.add(hwm_history_record)
                hwm_history_records.append(hwm_history_record)
        await async_session.commit()

    yield hwm_history_records

    for hwm in hwms:
        query = delete(HWMHistory).where(HWMHistory.hwm_id == hwm.id)
        async with async_session_factory() as async_session:
            await async_session.execute(query)
            await async_session.commit()

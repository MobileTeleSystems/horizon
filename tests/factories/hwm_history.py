# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.backend.db.models import HWM, HWMHistory, Namespace, User
from tests.factories.base import random_datetime, random_string


def hwm_history_factory(**kwargs):
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
    return HWMHistory(**data)


@pytest_asyncio.fixture(params=[(5, {})])
async def hwm_history_items(
    user: User,
    namespace: Namespace,
    hwm: HWM,
    request: pytest.FixtureRequest,
    async_session: AsyncSession,
) -> AsyncGenerator[list[HWMHistory], None]:
    size, params = request.param
    result = [
        hwm_history_factory(namespace_id=namespace.id, hwm_id=hwm.id, changed_by_user_id=user.id, **params)
        for _ in range(size)
    ]
    for item in result:
        async_session.add(item)

    # this is not required for backend tests, but needed by client tests
    await async_session.commit()

    for item in result:
        # before removing object from Session load all relationships
        await async_session.refresh(item, attribute_names=["changed_by_user"])
        async_session.expunge(item)

    yield result

    query = delete(HWMHistory).where(HWMHistory.hwm_id == hwm.id)
    await async_session.execute(query)
    await async_session.commit()

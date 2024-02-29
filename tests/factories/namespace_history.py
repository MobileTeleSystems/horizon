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

from horizon.backend.db.models import Namespace, NamespaceHistory, User
from tests.factories.base import random_string


def namespace_history_factory(**kwargs):
    data = {
        "id": randint(0, 10000000),
        "name": random_string(),
        "description": random_string(),
        "changed_at": datetime.now(timezone.utc),
        "owner_id": randint(0, 10000000),
        "action": "Created",
    }
    data.update(kwargs)
    return NamespaceHistory(**data)


@pytest_asyncio.fixture(params=[(5, {})])
async def namespace_history_items(
    user: User,
    namespace: Namespace,
    request: pytest.FixtureRequest,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[list[NamespaceHistory], None]:
    size, params = request.param
    result = [
        namespace_history_factory(namespace_id=namespace.id, changed_by_user_id=user.id, owner_id=user.id, **params)
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
            await async_session.refresh(item, attribute_names=["changed_by_user", "owner"])
            async_session.expunge(item)

    yield result

    query = delete(NamespaceHistory).where(NamespaceHistory.namespace_id == namespace.id)
    async with async_session_factory() as async_session:
        await async_session.execute(query)
        await async_session.commit()

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from collections.abc import AsyncGenerator
from random import randint

import pytest
import pytest_asyncio
from polyfactory import Ignore, Use
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.db.models import HWM, HWMHistory, Namespace, User
from tests.factories.namespace import NamespaceFactory


class HWMHistoryFactory(SQLAlchemyFactory[HWMHistory]):
    __model__ = HWMHistory

    id = Ignore()
    namespace = Use(NamespaceFactory)
    is_deleted = False
    changed_at = Ignore()

    # for most cases use int as value, other types will be tested explicitly
    @classmethod
    def value(cls):
        return randint(100, 1000)  # noqa: S311


@pytest_asyncio.fixture(params=[(5, {})])
async def hwm_history_items(
    user: User,
    namespace: Namespace,
    hwm: HWM,
    request: pytest.FixtureRequest,
    async_session: AsyncSession,
) -> AsyncGenerator[list[HWMHistory], None]:
    HWMHistoryFactory.__async_session__ = async_session
    size, params = request.param
    result = await HWMHistoryFactory.create_batch_async(
        size,
        namespace_id=namespace.id,
        hwm_id=hwm.id,
        name=hwm.name,
        changed_by_user_id=user.id,
        **params,
    )
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

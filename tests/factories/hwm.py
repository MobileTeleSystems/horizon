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

from horizon.db.models import HWM, Namespace, User
from tests.factories.namespace import NamespaceFactory
from tests.factories.user import UserFactory


class HWMFactory(SQLAlchemyFactory[HWM]):
    __model__ = HWM

    id = Ignore()
    namespace = Use(NamespaceFactory)
    is_deleted = False
    changed_by_user = Use(UserFactory)
    changed_at = Ignore()

    # for most cases use int as value, other types will be tested explicitly
    @classmethod
    def value(cls):
        return randint(100, 1000)  # noqa: S311


@pytest_asyncio.fixture(params=[{}])
async def new_hwm(request: pytest.FixtureRequest, async_session: AsyncSession) -> AsyncGenerator[HWM, None]:
    params = request.param
    hwm = HWMFactory.build(**params)
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
    HWMFactory.__async_session__ = async_session
    params = request.param
    hwm = await HWMFactory.create_async(**params, namespace_id=namespace.id, changed_by_user_id=user.id)
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
    HWMFactory.__async_session__ = async_session
    size, params = request.param
    result = await HWMFactory.create_batch_async(size, **params, namespace_id=namespace.id, changed_by_user_id=user.id)
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

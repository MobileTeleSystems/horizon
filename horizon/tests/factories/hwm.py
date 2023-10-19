from collections.abc import AsyncGenerator
from random import randint

import pytest
import pytest_asyncio
from polyfactory import Ignore, Use
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import HWM, Namespace, User
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
async def new_hwm(request: pytest.FixtureRequest, session: AsyncSession) -> AsyncGenerator[HWM, None]:
    params = request.param
    hwm = HWMFactory.build(**params)
    yield hwm

    query = delete(HWM).where(HWM.name == hwm.name)
    await session.execute(query)
    await session.commit()


@pytest_asyncio.fixture(params=[{}])
async def hwm(
    user: User,
    namespace: Namespace,
    request: pytest.FixtureRequest,
    session: AsyncSession,
) -> AsyncGenerator[HWM, None]:
    HWMFactory.__async_session__ = session
    params = request.param
    hwm = await HWMFactory.create_async(**params, namespace_id=namespace.id, changed_by_user_id=user.id)

    # remove current object from Session. this is required to compare object against new state fetched
    # from database, and also to remove it from cache
    hwm_id = hwm.id
    await session.refresh(hwm, attribute_names=["changed_by_user", "namespace"])
    session.expunge(hwm)
    yield hwm

    query = delete(HWM).where(HWM.id == hwm_id)
    await session.execute(query)
    await session.commit()


@pytest_asyncio.fixture(params=[(5, {})])
async def hwms(
    user: User,
    namespace: Namespace,
    request: pytest.FixtureRequest,
    session: AsyncSession,
) -> AsyncGenerator[list[HWM], None]:
    HWMFactory.__async_session__ = session
    size, params = request.param
    result = await HWMFactory.create_batch_async(size, **params, namespace_id=namespace.id, changed_by_user_id=user.id)

    hwm_ids = []
    for item in result:
        hwm_ids.append(item.id)
        # before removing object from Session load all relationships
        await session.refresh(item, attribute_names=["changed_by_user", "namespace"])
        session.expunge(item)

    yield result

    query = delete(HWM).where(HWM.id.in_(hwm_ids))
    await session.execute(query)
    await session.commit()

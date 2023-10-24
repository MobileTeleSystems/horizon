# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from polyfactory import Ignore, Use
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.db.models.namespace import Namespace
from horizon.db.models.user import User
from tests.factories.user import UserFactory


class NamespaceFactory(SQLAlchemyFactory[Namespace]):
    __model__ = Namespace

    id = Ignore()
    is_deleted = False
    changed_by_user = Use(UserFactory)
    changed_at = Ignore()


@pytest_asyncio.fixture(params=[{}])
async def new_namespace(request: pytest.FixtureRequest, session: AsyncSession) -> AsyncGenerator[Namespace, None]:
    params = request.param
    namespace = NamespaceFactory.build(**params)
    yield namespace

    query = delete(Namespace).where(Namespace.name == namespace.name)
    await session.execute(query)
    await session.commit()


@pytest_asyncio.fixture(params=[{}])
async def namespace(
    user: User,
    request: pytest.FixtureRequest,
    session: AsyncSession,
) -> AsyncGenerator[Namespace, None]:
    NamespaceFactory.__async_session__ = session
    params = request.param
    namespace = await NamespaceFactory.create_async(**params, changed_by_user_id=user.id)

    # remove current object from Session. this is required to compare object against new state fetched
    # from database, and also to remove it from cache
    namespace_id = namespace.id
    await session.refresh(namespace, attribute_names=["changed_by_user"])
    session.expunge(namespace)
    yield namespace

    query = delete(Namespace).where(Namespace.id == namespace_id)
    await session.execute(query)
    await session.commit()


@pytest_asyncio.fixture(params=[(5, {})])
async def namespaces(
    user: User,
    request: pytest.FixtureRequest,
    session: AsyncSession,
) -> AsyncGenerator[list[Namespace], None]:
    NamespaceFactory.__async_session__ = session
    size, params = request.param
    result = await NamespaceFactory.create_batch_async(size, **params, changed_by_user_id=user.id)

    namespace_ids = []
    for item in result:
        namespace_ids.append(item.id)
        # before removing object from Session load all relationships
        await session.refresh(item, attribute_names=["changed_by_user"])
        session.expunge(item)

    yield result

    query = delete(Namespace).where(Namespace.id.in_(namespace_ids))
    await session.execute(query)
    await session.commit()

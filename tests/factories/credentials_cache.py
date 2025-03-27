from __future__ import annotations

from random import randint
from typing import TYPE_CHECKING, AsyncContextManager, Callable

import pytest  # noqa: TC002
import pytest_asyncio
from passlib.hash import argon2
from sqlalchemy import delete

from horizon.backend.db.models import CredentialsCache
from tests.factories.base import random_string

if TYPE_CHECKING:
    from typing import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncSession

    from horizon.backend.db.models.user import User


def credentials_cache_factory(**kwargs):
    data = {
        "id": randint(0, 10000000),
        "login": random_string(),
        "password_hash": argon2.hash(random_string()),
    }
    data.update(kwargs)
    return CredentialsCache(**data)


@pytest_asyncio.fixture(params=[{}])
async def credentials_cache_item(
    user: User,
    request: pytest.FixtureRequest,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[CredentialsCache, None]:
    params = request.param
    item = credentials_cache_factory(user_id=user.id, **params)

    # do not use the same session in tests and fixture teardown
    # see https://github.com/MobileTeleSystems/horizon/pull/6
    async with async_session_factory() as async_session:
        async_session.add(item)
        # this is not required for backend tests, but needed by client tests
        await async_session.commit()

        # remove current object from async_session. this is required to compare object against new state fetched
        # from database, and also to remove it from cache
        item_id = item.id
        async_session.expunge(item)

    yield item

    query = delete(CredentialsCache).where(CredentialsCache.id == item_id)
    async with async_session_factory() as async_session:
        await async_session.execute(query)
        await async_session.commit()

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from passlib.hash import argon2
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.backend.db.models import CredentialsCache
from horizon.backend.db.models.user import User
from tests.factories.base import random_string


def credentials_cache_factory(**kwargs):
    data = {
        "login": random_string(),
        "password_hash": argon2.hash(random_string()),
    }
    data.update(kwargs)
    return CredentialsCache(**data)


@pytest_asyncio.fixture(params=[{}])
async def credentials_cache_item(
    user: User, request: pytest.FixtureRequest, async_session: AsyncSession
) -> AsyncGenerator[CredentialsCache, None]:
    params = request.param
    result = credentials_cache_factory(user_id=user.id, **params)
    async_session.add(result)
    # this is not required for backend tests, but needed by client tests
    await async_session.commit()

    # remove current object from async_session. this is required to compare object against new state fetched
    # from database, and also to remove it from cache
    item_id = result.id
    async_session.expunge(result)
    yield result

    query = delete(CredentialsCache).where(CredentialsCache.id == item_id)
    await async_session.execute(query)
    await async_session.commit()

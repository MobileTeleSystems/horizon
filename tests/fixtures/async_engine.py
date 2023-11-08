# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import contextlib
from collections.abc import AsyncGenerator
from typing import TYPE_CHECKING

import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine

    from horizon.backend.settings import Settings


@contextlib.asynccontextmanager
async def get_async_engine(settings: Settings) -> AsyncGenerator[AsyncEngine, None]:
    """Create test engine"""
    connection_url = settings.database.url
    engine = create_async_engine(connection_url, echo=True)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def async_engine(settings: Settings):
    async with get_async_engine(settings) as result:
        yield result

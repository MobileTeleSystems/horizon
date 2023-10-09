from __future__ import annotations

from typing import TYPE_CHECKING

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncEngine


@pytest_asyncio.fixture(scope="session")
async def sessionmaker(engine: AsyncEngine):
    yield async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
    )


@pytest_asyncio.fixture
async def session(sessionmaker: async_sessionmaker[AsyncSession]):
    try:
        session: AsyncSession = sessionmaker()
        yield session
    finally:
        await session.close()

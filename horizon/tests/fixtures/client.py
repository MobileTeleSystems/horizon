from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient

from app.main import application_factory
from app.settings import Settings


@pytest_asyncio.fixture(scope="session")
async def client(settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    app = application_factory(settings=settings)
    async with AsyncClient(app=app, base_url="http://horizon") as result:
        yield result

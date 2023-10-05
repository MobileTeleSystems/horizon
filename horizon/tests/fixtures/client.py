from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient

from app.main import application_factory


@pytest_asyncio.fixture(scope="session")
async def client(settings) -> AsyncGenerator[AsyncClient, None]:
    app = application_factory(settings=settings)
    async with AsyncClient(app=app, base_url="http://horizon") as result:
        yield result

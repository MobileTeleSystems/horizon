# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from collections.abc import AsyncGenerator

import pytest_asyncio
from httpx import AsyncClient

from horizon.main import application_factory
from horizon.settings import Settings


@pytest_asyncio.fixture(scope="session")
async def client(settings: Settings) -> AsyncGenerator[AsyncClient, None]:
    app = application_factory(settings=settings)
    async with AsyncClient(app=app, base_url="http://horizon") as result:
        yield result

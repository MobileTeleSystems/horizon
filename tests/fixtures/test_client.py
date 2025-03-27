from __future__ import annotations

from typing import TYPE_CHECKING

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

if TYPE_CHECKING:
    from typing import AsyncGenerator

    from fastapi import FastAPI


@pytest_asyncio.fixture
async def test_client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=test_app)
    async with AsyncClient(transport=transport, base_url="http://horizon") as result:
        yield result

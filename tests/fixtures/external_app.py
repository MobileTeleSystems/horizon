# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from horizon_client.auth import AccessToken, OAuth2Password

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from horizon.db.models import User


@pytest.fixture(scope="session")
def external_app_url() -> str:
    return os.environ["HORIZON_TEST_SERVER_URL"]


@pytest.fixture
def app_oauth2_password(new_user: User) -> OAuth2Password:
    return OAuth2Password(username=new_user.username, password="test")


@pytest_asyncio.fixture
async def app_access_token(async_session: AsyncSession, access_token: str) -> AccessToken:
    return AccessToken(token=access_token)

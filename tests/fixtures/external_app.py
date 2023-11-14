# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import os
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio

from horizon.client.auth import AccessToken, LoginPassword

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from horizon.backend.db.models import User


@pytest.fixture(scope="session")
def external_app_url() -> str:
    return os.environ["HORIZON_TEST_SERVER_URL"]

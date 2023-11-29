# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import pytest
from httpx import AsyncClient

from horizon.backend.db.models import User

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


# other negative tests can be found in DummyAuthProvider & LDAPAuthProvider tests
async def test_whoami_anonymous_user(test_client: AsyncClient):
    response = await test_client.get("v1/users/me")
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_whoami(
    test_client: AsyncClient,
    access_token: str,
    user: User,
):
    response = await test_client.get(
        "v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": user.id,
        "username": user.username,
    }

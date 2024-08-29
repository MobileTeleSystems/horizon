# SPDX-FileCopyrightText: 2023 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
import pytest
from httpx import AsyncClient

from horizon.backend.db.models import NamespaceUserRoleInt, User

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


@pytest.mark.parametrize(
    "user_with_role",
    [
        NamespaceUserRoleInt.SUPERADMIN,
    ],
    indirect=["user_with_role"],
)
async def test_whoami_superadmin(
    test_client: AsyncClient,
    access_token: str,
    user_with_role: None,
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
        "is_admin": True,
    }

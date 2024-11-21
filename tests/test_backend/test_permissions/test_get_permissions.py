# SPDX-FileCopyrightText: 2023 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.backend.db.models import Namespace, NamespaceUserRoleInt, User

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_get_namespace_permissions_unauthorized_user(
    test_client: AsyncClient,
    namespace: Namespace,
):
    response = await test_client.get(
        f"/v1/namespaces/{namespace.id}/permissions",
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_get_namespace_permissions_missing(
    test_client: AsyncClient,
    access_token: str,
    new_namespace: Namespace,
):
    response = await test_client.get(
        f"/v1/namespaces/{new_namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"Namespace with id={new_namespace.id!r} not found",
            "details": {
                "entity_type": "Namespace",
                "field": "id",
                "value": new_namespace.id,
            },
        },
    }


@pytest.mark.parametrize("user_with_role", [NamespaceUserRoleInt.OWNER], indirect=["user_with_role"])
@pytest.mark.parametrize(
    "namespace_with_users",
    [
        [
            ("user1", NamespaceUserRoleInt.DEVELOPER),
            ("user2", NamespaceUserRoleInt.DEVELOPER),
            ("user3", NamespaceUserRoleInt.MAINTAINER),
        ],
    ],
    indirect=["namespace_with_users"],
)
async def test_get_namespace_permissions(
    test_client: AsyncClient,
    access_token: str,
    user_with_role: None,
    namespace_with_users: None,
    user: User,
    namespace: Namespace,
):
    response = await test_client.get(
        f"/v1/namespaces/{namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    assert response.json() == {
        "permissions": [
            {"username": user.username, "role": "OWNER"},
            {"username": "user3", "role": "MAINTAINER"},
            {"username": "user1", "role": "DEVELOPER"},
            {"username": "user2", "role": "DEVELOPER"},
        ],
    }


@pytest.mark.parametrize(
    "user_with_role, expected_status, expected_response",
    [
        (
            NamespaceUserRoleInt.MAINTAINER,
            403,
            {
                "error": {
                    "code": "permission_denied",
                    "message": "Permission denied. User has role MAINTAINER but action requires at least OWNER.",
                    "details": {
                        "required_role": "OWNER",
                        "actual_role": "MAINTAINER",
                    },
                },
            },
        ),
        (
            NamespaceUserRoleInt.DEVELOPER,
            403,
            {
                "error": {
                    "code": "permission_denied",
                    "message": "Permission denied. User has role DEVELOPER but action requires at least OWNER.",
                    "details": {
                        "required_role": "OWNER",
                        "actual_role": "DEVELOPER",
                    },
                },
            },
        ),
        (
            NamespaceUserRoleInt.GUEST,
            403,
            {
                "error": {
                    "code": "permission_denied",
                    "message": "Permission denied. User has role GUEST but action requires at least OWNER.",
                    "details": {
                        "required_role": "OWNER",
                        "actual_role": "GUEST",
                    },
                },
            },
        ),
    ],
    indirect=["user_with_role"],
)
async def test_get_permissions_denied(
    namespace: Namespace,
    user_with_role: None,
    expected_status: int,
    expected_response: dict,
    test_client: AsyncClient,
    access_token: str,
):
    response = await test_client.get(
        f"v1/namespaces/{namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response

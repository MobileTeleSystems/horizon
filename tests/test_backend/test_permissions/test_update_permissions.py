# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

import pytest
from pydantic import __version__ as pydantic_version

from horizon.backend.db.models import Namespace, NamespaceUserRoleInt, User

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_update_namespace_permissions_unauthorized_user(
    test_client: AsyncClient,
    namespace: Namespace,
):
    changes = {
        "permissions": [
            {"username": secrets.token_hex(6), "role": NamespaceUserRoleInt.DEVELOPER.name},
        ],
    }
    response = await test_client.patch(
        f"/v1/namespaces/{namespace.id}/permissions",
        json=changes,
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_update_namespace_permissions_namespace_missing(
    test_client: AsyncClient,
    access_token: str,
    new_namespace: Namespace,
):
    changes = {
        "permissions": [
            {"username": secrets.token_hex(6), "role": NamespaceUserRoleInt.DEVELOPER.name},
        ],
    }
    response = await test_client.patch(
        f"/v1/namespaces/{new_namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
        json=changes,
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
async def test_update_namespace_permissions_with_duplicates_usernames(
    test_client: AsyncClient,
    access_token: str,
    namespace_with_users: None,
    namespace: Namespace,
):
    changes = {
        "permissions": [
            {"username": "user1", "role": "DEVELOPER"},
            {"username": "user1", "role": "MAINTAINER"},
            {"username": "user2", "role": "OWNER"},
        ],
    }
    response = await test_client.patch(
        f"/v1/namespaces/{namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
        json=changes,
    )
    assert response.status_code == 422

    if pydantic_version >= "2":
        detail = {
            "code": "value_error",
            "context": {},
            "input": [
                {"role": "DEVELOPER", "username": "user1"},
                {"role": "MAINTAINER", "username": "user1"},
                {"role": "OWNER", "username": "user2"},
            ],
            "location": ["body", "permissions"],
            "message": "Value error, Duplicate username detected: user1. Each username must appear only once.",
        }
    else:
        detail = {
            "code": "value_error",
            "location": ["body", "permissions"],
            "message": "Duplicate username detected: user1. Each username must appear only once.",
        }

    expected_body = {
        "error": {
            "code": "invalid_request",
            "details": [detail],
            "message": "Invalid request",
        },
    }

    assert response.json() == expected_body


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
async def test_update_namespace_permissions_duplicates_owner(
    test_client: AsyncClient,
    access_token: str,
    namespace_with_users: None,
    namespace: Namespace,
):
    changes = {
        "permissions": [
            {"username": "user1", "role": "DEVELOPER"},
            {"username": "user2", "role": "OWNER"},
            {"username": "user3", "role": "OWNER"},
        ],
    }
    response = await test_client.patch(
        f"/v1/namespaces/{namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
        json=changes,
    )
    assert response.status_code == 422

    if pydantic_version >= "2":
        detail = {
            "code": "value_error",
            "context": {},
            "input": changes["permissions"],
            "location": ["body", "permissions"],
            "message": "Value error, Multiple owner role assignments detected. Only one owner can be assigned.",
        }
    else:
        detail = {
            "code": "value_error",
            "location": ["body", "permissions"],
            "message": "Multiple owner role assignments detected. Only one owner can be assigned.",
        }

    expected_body = {
        "error": {
            "code": "invalid_request",
            "details": [detail],
            "message": "Invalid request",
        },
    }

    assert response.json() == expected_body


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
async def test_update_namespace_permissions_lose_owner(
    test_client: AsyncClient,
    access_token: str,
    user: User,
    namespace_with_users: None,
    namespace: Namespace,
):
    changes = {
        "permissions": [
            {"username": user.username, "role": "DEVELOPER"},
        ],
    }
    response = await test_client.patch(
        f"/v1/namespaces/{namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
        json=changes,
    )
    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "bad_request",
            "message": "Cannot drop ownership without assigning a new owner.",
            "details": {},
        },
    }


@pytest.mark.parametrize(
    "namespace_with_users",
    [
        [
            ("user1", NamespaceUserRoleInt.DEVELOPER),
            ("user2", NamespaceUserRoleInt.MAINTAINER),
            ("user3", NamespaceUserRoleInt.DEVELOPER),
        ],
    ],
    indirect=["namespace_with_users"],
)
async def test_update_namespace_permissions_remove_role(
    test_client: AsyncClient,
    access_token: str,
    namespace_with_users: None,
    namespace: Namespace,
    user: User,
):
    changes = {
        "permissions": [
            {"username": "user3", "role": None},
        ],
    }
    response = await test_client.patch(
        f"/v1/namespaces/{namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
        json=changes,
    )
    assert response.status_code == 200
    assert response.json() == {
        "permissions": [
            {"username": user.username, "role": "OWNER"},
            {"username": "user2", "role": "MAINTAINER"},
            {"username": "user1", "role": "DEVELOPER"},
        ],
    }


@pytest.mark.parametrize(
    "namespace_with_users",
    [
        [
            ("user1", NamespaceUserRoleInt.DEVELOPER),
            ("user2", NamespaceUserRoleInt.MAINTAINER),
        ],
    ],
    indirect=["namespace_with_users"],
)
async def test_update_namespace_permissions_add_or_update_roles(
    test_client: AsyncClient,
    access_token: str,
    namespace_with_users: None,
    namespace: Namespace,
    user: User,
):
    changes = {
        "permissions": [
            {"username": "user1", "role": "MAINTAINER"},
            {"username": "user2", "role": "DEVELOPER"},
        ],
    }

    response = await test_client.patch(
        f"/v1/namespaces/{namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
        json=changes,
    )

    assert response.status_code == 200
    assert response.json() == {
        "permissions": [
            {"username": user.username, "role": "OWNER"},
            {"username": "user1", "role": "MAINTAINER"},
            {"username": "user2", "role": "DEVELOPER"},
        ],
    }


@pytest.mark.parametrize(
    "namespace_with_users",
    [
        [
            ("existing_owner", NamespaceUserRoleInt.OWNER),
            ("user_to_become_owner", NamespaceUserRoleInt.DEVELOPER),
            ("other_user", NamespaceUserRoleInt.DEVELOPER),
        ],
    ],
    indirect=["namespace_with_users"],
)
async def test_update_namespace_permissions_change_owner(
    test_client: AsyncClient,
    access_token: str,
    namespace_with_users: None,
    namespace: Namespace,
):
    changes = {
        "permissions": [
            {"username": "user_to_become_owner", "role": "OWNER"},
        ],
    }

    response = await test_client.patch(
        f"/v1/namespaces/{namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
        json=changes,
    )

    assert response.status_code == 200
    assert response.json() == {
        "permissions": [
            {"username": "user_to_become_owner", "role": "OWNER"},
            {"username": "other_user", "role": "DEVELOPER"},
        ],
    }


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
async def test_update_namespace_permissions_unknown_user(
    test_client: AsyncClient,
    access_token: str,
    namespace_with_users: None,
    namespace: Namespace,
    new_user: User,
):
    changes = {
        "permissions": [
            {"username": new_user.username, "role": "DEVELOPER"},
        ],
    }

    response = await test_client.patch(
        f"/v1/namespaces/{namespace.id}/permissions",
        headers={"Authorization": f"Bearer {access_token}"},
        json=changes,
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"User with username={new_user.username!r} not found",
            "details": {
                "entity_type": "User",
                "field": "username",
                "value": new_user.username,
            },
        },
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
async def test_update_permissions_denied(
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

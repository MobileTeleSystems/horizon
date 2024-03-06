# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Tuple

import pytest
from pydantic import __version__ as pydantic_version
from sqlalchemy import select
from sqlalchemy_utils.functions import naturally_equivalent

from horizon.backend.db.models import (
    Namespace,
    NamespaceHistory,
    NamespaceUserRole,
    User,
)

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_update_namespace_anonymous_user(
    test_client: AsyncClient,
    namespace: Namespace,
):
    response = await test_client.patch(
        f"v1/namespaces/{namespace.id}",
        json={
            "name": secrets.token_hex(16),
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_update_namespace_missing(
    test_client: AsyncClient,
    access_token: str,
    new_namespace: Namespace,
):
    response = await test_client.patch(
        f"v1/namespaces/{new_namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": secrets.token_hex(16),
        },
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
    "new_namespace",
    [
        pytest.param({"name": "a" * 256}, id="max-name"),
    ],
    indirect=True,
)
async def test_update_namespace_name(
    test_client: AsyncClient,
    access_token: str,
    user: User,
    namespace: Namespace,
    new_namespace: Namespace,
    async_session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await test_client.patch(
        f"v1/namespaces/{namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": new_namespace.name,
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["id"]
    assert content["name"] == new_namespace.name
    assert content["description"] == namespace.description
    assert content["changed_by"] == user.username

    changed_at = datetime.fromisoformat(content["changed_at"].replace("Z", "+00:00"))
    assert changed_at >= current_dt >= namespace.changed_at

    query = select(Namespace).where(Namespace.id == namespace.id)
    query_result = await async_session.scalars(query)
    namespace_after = query_result.one()

    # Row is same as in body
    assert namespace_after.name == content["name"]
    assert namespace_after.description == content["description"]
    assert namespace_after.changed_at == changed_at
    assert namespace_after.changed_by_user_id == user.id

    query = select(NamespaceHistory).where(NamespaceHistory.namespace_id == namespace.id)
    query_result = await async_session.scalars(query)
    updated_namespace_history = query_result.one()

    # Row is same as in body
    assert updated_namespace_history.name == content["name"]
    assert updated_namespace_history.namespace_id == namespace.id
    assert updated_namespace_history.description == content["description"]
    assert updated_namespace_history.changed_at == changed_at
    assert updated_namespace_history.changed_by_user_id == user.id
    assert updated_namespace_history.action == "Updated"


@pytest.mark.parametrize(
    "user_with_role",
    [(NamespaceUserRole.OWNER,)],
    indirect=["user_with_role"],
)
async def test_update_namespace_description(
    test_client: AsyncClient,
    access_token: str,
    user_with_role: Tuple[User, Namespace],
    new_namespace: Namespace,
    async_session: AsyncSession,
):
    user, namespace = user_with_role
    current_dt = datetime.now(tz=timezone.utc)
    response = await test_client.patch(
        f"v1/namespaces/{namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "description": new_namespace.description,
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["id"]
    assert content["name"] == namespace.name
    assert content["description"] == new_namespace.description
    assert content["changed_by"] == user.username

    changed_at = datetime.fromisoformat(content["changed_at"].replace("Z", "+00:00"))
    assert changed_at >= current_dt >= namespace.changed_at

    query = select(Namespace).where(Namespace.id == namespace.id)
    query_result = await async_session.scalars(query)
    namespace_after = query_result.one()

    # Row is same as in body
    assert namespace_after.name == content["name"]
    assert namespace_after.description == content["description"]
    assert namespace_after.changed_at == changed_at
    assert namespace_after.changed_by_user_id == user.id

    query = select(NamespaceHistory).where(NamespaceHistory.namespace_id == namespace.id)
    query_result = await async_session.scalars(query)
    updated_namespace_history = query_result.one()

    # Row is same as in body
    assert updated_namespace_history.name == content["name"]
    assert updated_namespace_history.namespace_id == namespace.id
    assert updated_namespace_history.description == content["description"]
    assert updated_namespace_history.changed_at == changed_at
    assert updated_namespace_history.changed_by_user_id == user.id
    assert updated_namespace_history.action == "Updated"


@pytest.mark.parametrize(
    "settings",
    [
        {"server": {"debug": True}},
        {"server": {"debug": False}},
    ],
    indirect=True,
)
async def test_update_namespace_no_data(
    test_client: AsyncClient,
    access_token: str,
    namespace: Namespace,
):
    response = await test_client.patch(
        f"v1/namespaces/{namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"unexpected": "value"},
    )
    assert response.status_code == 422

    details: list[dict[str, Any]]
    if pydantic_version < "2":
        details = [
            {
                "location": ["body", "__root__"],
                "code": "value_error",
                "message": "At least one field must be set.",
            }
        ]
    else:
        details = [
            {
                "location": ["body"],
                "code": "value_error",
                "message": "Value error, At least one field must be set.",
                "context": {},
                "input": {"unexpected": "value"},
                "url": "https://errors.pydantic.dev/2.5/v/value_error",
            }
        ]

    assert response.json() == {
        "error": {
            "code": "invalid_request",
            "message": "Invalid request",
            "details": details,
        }
    }


async def test_update_namespace_duplicated_name(
    test_client: AsyncClient,
    access_token: str,
    namespaces: list[Namespace],
    async_session: AsyncSession,
):
    namespace1, namespace2, *_ = namespaces

    response = await test_client.patch(
        f"v1/namespaces/{namespace1.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": namespace2.name,
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "already_exists",
            "message": f"Namespace with name={namespace2.name!r} already exists",
            "details": {
                "entity_type": "Namespace",
                "field": "name",
                "value": namespace2.name,
            },
        },
    }

    query = select(Namespace).where(Namespace.id == namespace1.id)
    query_result = await async_session.scalars(query)
    namespace1_after = query_result.one()

    # Nothing is changed
    assert naturally_equivalent(namespace1_after, namespace1)


@pytest.mark.parametrize(
    "new_namespace",
    [
        pytest.param({"name": ""}, id="empty-name"),
        pytest.param({"name": "a" * 257}, id="too-long-name"),
    ],
    indirect=True,
)
async def test_update_namespace_invalid_name_length(
    test_client: AsyncClient,
    access_token: str,
    namespace: Namespace,
    new_namespace: Namespace,
    async_session: AsyncSession,
):
    response = await test_client.patch(
        f"v1/namespaces/{namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": new_namespace.name},
    )

    details: list[dict[str, Any]]
    if pydantic_version < "2":
        if len(new_namespace.name) > 256:
            details = [
                {
                    "location": ["body", "name"],
                    "message": "ensure this value has at most 256 characters",
                    "code": "value_error.any_str.max_length",
                },
                {
                    "location": ["body", "name"],
                    "message": "instance of Unset expected",
                    "code": "type_error.arbitrary_type",
                },
            ]
        else:
            details = [
                {
                    "location": ["body", "name"],
                    "message": "ensure this value has at least 1 characters",
                    "code": "value_error.any_str.min_length",
                },
                {
                    "location": ["body", "name"],
                    "message": "instance of Unset expected",
                    "code": "type_error.arbitrary_type",
                },
            ]
    else:
        if len(new_namespace.name) > 256:
            details = [
                {
                    "location": ["body", "name"],
                    "message": "Value should have at most 256 items after validation, not 257",
                    "code": "too_long",
                    "url": "https://errors.pydantic.dev/2.5/v/too_long",
                    "context": {"max_length": 256, "actual_length": 257, "field_type": "Value"},
                    "input": new_namespace.name,
                },
            ]
        else:
            details = [
                {
                    "location": ["body", "name"],
                    "message": "Value should have at least 1 item after validation, not 0",
                    "code": "too_short",
                    "url": "https://errors.pydantic.dev/2.5/v/too_short",
                    "context": {"min_length": 1, "actual_length": 0, "field_type": "Value"},
                    "input": "",
                },
            ]

    expected = {
        "error": {
            "code": "invalid_request",
            "message": "Invalid request",
            "details": details,
        },
    }

    assert response.status_code == 422
    assert response.json() == expected

    query = select(Namespace).where(Namespace.id == namespace.id)
    query_result = await async_session.scalars(query)
    namespace_after = query_result.one()

    # Nothing is changed
    assert naturally_equivalent(namespace_after, namespace)


@pytest.mark.parametrize(
    "user_with_role, expected_status, expected_response",
    [
        (
            (NamespaceUserRole.MAINTAINER,),
            403,
            {
                "error": {
                    "code": "permission_denied",
                    "message": f"Permission denied as user lacks {NamespaceUserRole.OWNER.name} role. Actual role is {NamespaceUserRole.MAINTAINER.name}",
                    "details": {
                        "required_role": NamespaceUserRole.OWNER.name,
                        "actual_role": NamespaceUserRole.MAINTAINER.name,
                    },
                }
            },
        ),
        (
            (NamespaceUserRole.DEVELOPER,),
            403,
            {
                "error": {
                    "code": "permission_denied",
                    "message": f"Permission denied as user lacks {NamespaceUserRole.OWNER.name} role. Actual role is {NamespaceUserRole.DEVELOPER.name}",
                    "details": {
                        "required_role": NamespaceUserRole.OWNER.name,
                        "actual_role": NamespaceUserRole.DEVELOPER.name,
                    },
                }
            },
        ),
        (
            (NamespaceUserRole.AUTHORIZED,),
            403,
            {
                "error": {
                    "code": "permission_denied",
                    "message": f"Permission denied as user lacks {NamespaceUserRole.OWNER.name} role. Actual role is {NamespaceUserRole.AUTHORIZED.name}",
                    "details": {
                        "required_role": NamespaceUserRole.OWNER.name,
                        "actual_role": NamespaceUserRole.AUTHORIZED.name,
                    },
                }
            },
        ),
    ],
    indirect=["user_with_role"],
)
async def test_update_namespace_permission_denied(
    user_with_role: Tuple[User, Namespace],
    expected_status: int,
    expected_response: dict,
    test_client: AsyncClient,
    access_token: str,
):
    user, namespace = user_with_role
    response = await test_client.patch(
        f"v1/namespaces/{namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": namespace.name,
        },
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response

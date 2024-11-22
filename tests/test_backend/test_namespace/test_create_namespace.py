from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import __version__ as pydantic_version
from sqlalchemy import desc, select
from sqlalchemy_utils.functions import naturally_equivalent

from horizon.backend.db.models import Namespace, NamespaceHistory, User

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_create_namespace_anonymous_user(
    test_client: AsyncClient,
):
    response = await test_client.post(
        "v1/namespaces/",
        json={
            "name": "test",
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


@pytest.mark.parametrize(
    "new_namespace",
    [
        pytest.param({"name": "a" * 256}, id="max-name"),
    ],
    indirect=True,
)
async def test_create_namespace(
    test_client: AsyncClient,
    access_token: str,
    user: User,
    new_namespace: Namespace,
    async_session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await test_client.post(
        "v1/namespaces/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": new_namespace.name,
            "description": new_namespace.description,
        },
    )
    assert response.status_code == 201

    content = response.json()
    namespace_id = content["id"]
    assert namespace_id
    assert content["name"] == new_namespace.name
    assert content["description"] == new_namespace.description
    assert content["changed_by"] == user.username

    changed_at = datetime.fromisoformat(content["changed_at"].replace("Z", "+00:00"))
    assert changed_at >= current_dt

    query = select(Namespace).where(Namespace.id == namespace_id)
    query_result = await async_session.scalars(query)
    created_namespace = query_result.one()

    # Row is same as in body
    assert created_namespace.name == content["name"]
    assert created_namespace.description == content["description"]
    assert created_namespace.changed_at == changed_at
    assert created_namespace.changed_by_user_id == user.id
    assert created_namespace.owner_id == user.id

    query = select(NamespaceHistory).where(NamespaceHistory.namespace_id == namespace_id)
    query_result = await async_session.scalars(query)
    created_namespace_history = query_result.one()

    # Row is same as in body
    assert created_namespace_history.name == content["name"]
    assert created_namespace_history.description == content["description"]
    assert created_namespace_history.changed_at == changed_at
    assert created_namespace_history.changed_by_user_id == user.id
    assert created_namespace_history.owner_id == user.id
    assert created_namespace_history.action == "Created"


async def test_create_namespace_duplicated_name(
    test_client: AsyncClient,
    access_token: str,
    namespace: Namespace,
    async_session: AsyncSession,
):
    response = await test_client.post(
        "v1/namespaces/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": namespace.name,
            "description": secrets.token_hex(16),
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "already_exists",
            "message": f"Namespace with name={namespace.name!r} already exists",
            "details": {
                "entity_type": "Namespace",
                "field": "name",
                "value": namespace.name,
            },
        },
    }

    query = select(Namespace).where(Namespace.id == namespace.id)
    query_result = await async_session.scalars(query)
    namespace_after = query_result.one()

    # Nothing is changed
    assert naturally_equivalent(namespace_after, namespace)


@pytest.mark.parametrize(
    "new_namespace",
    [
        pytest.param({"name": ""}, id="empty-name"),
        pytest.param({"name": "a" * 2049}, id="too-long-name"),
    ],
    indirect=True,
)
async def test_create_namespace_invalid_name_length(
    test_client: AsyncClient,
    new_namespace: Namespace,
    access_token: str,
    async_session: AsyncSession,
):
    response = await test_client.post(
        "v1/namespaces/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": new_namespace.name,
        },
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
            ]
        else:
            details = [
                {
                    "location": ["body", "name"],
                    "message": "ensure this value has at least 1 characters",
                    "code": "value_error.any_str.min_length",
                },
            ]
    else:
        if len(new_namespace.name) > 256:
            details = [
                {
                    "location": ["body", "name"],
                    "message": "String should have at most 256 characters",
                    "code": "string_too_long",
                    "context": {"max_length": 256},
                    "input": new_namespace.name,
                },
            ]
        else:
            details = [
                {
                    "location": ["body", "name"],
                    "message": "String should have at least 1 character",
                    "code": "string_too_short",
                    "context": {"min_length": 1},
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

    # Namespace is not created
    query = select(Namespace).where(Namespace.name == new_namespace.name)
    result = await async_session.scalars(query)
    created_namespace = result.one_or_none()

    assert not created_namespace


async def test_create_namespace_with_same_name_after_deletion(
    test_client: AsyncClient,
    access_token: str,
    new_namespace: Namespace,
    async_session: AsyncSession,
):
    namespace_data = {
        "name": new_namespace.name,
        "description": new_namespace.description,
    }
    create_response = await test_client.post(
        "/v1/namespaces/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=namespace_data,
    )
    assert create_response.status_code == 201
    old_namespace_id = create_response.json()["id"]

    delete_response = await test_client.delete(
        f"/v1/namespaces/{old_namespace_id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert delete_response.status_code == 204
    result = await async_session.execute(
        select(NamespaceHistory)
        .where(NamespaceHistory.namespace_id == old_namespace_id)
        .order_by(desc(NamespaceHistory.id)),
    )
    deleted_namespace_history = result.scalars().first()
    assert deleted_namespace_history.action == "Deleted"

    recreate_response = await test_client.post(
        "/v1/namespaces/",
        headers={"Authorization": f"Bearer {access_token}"},
        json=namespace_data,
    )
    assert recreate_response.status_code == 201

    new_namespace_id = recreate_response.json()["id"]
    assert new_namespace_id != old_namespace_id

    query = select(Namespace).where(Namespace.id == old_namespace_id)
    result = await async_session.execute(query)
    namespace_records = result.scalars().all()
    assert len(namespace_records) == 0

    query = select(Namespace).where(Namespace.id == new_namespace_id)
    result = await async_session.execute(query)
    recreated_namespace = result.scalars().first()
    assert recreated_namespace is not None

    result = await async_session.execute(
        select(NamespaceHistory).where(NamespaceHistory.namespace_id == new_namespace_id),
    )
    created_namespace_history = result.scalars().first()
    assert created_namespace_history.action == "Created"
    assert created_namespace_history.name == new_namespace.name
    assert created_namespace_history.name == namespace_data["name"]
    assert created_namespace_history.description == namespace_data["description"]

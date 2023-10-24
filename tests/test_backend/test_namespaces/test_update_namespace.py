# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import secrets
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select
from sqlalchemy_utils.functions import naturally_equivalent

from horizon.db.models import Namespace, User

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.asyncio]


async def test_update_namespace_anonymous_user(
    client: AsyncClient,
    namespace: Namespace,
):
    response = await client.patch(
        f"v1/namespaces/{namespace.name}",
        json={
            "name": secrets.token_hex(16),
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
        },
    }


async def test_update_namespace_missing(
    client: AsyncClient,
    access_token: str,
    new_namespace: Namespace,
):
    response = await client.patch(
        f"v1/namespaces/{new_namespace.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": secrets.token_hex(16),
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"Namespace with name='{new_namespace.name}' not found",
            "details": {
                "entity_type": "Namespace",
                "field": "name",
                "value": new_namespace.name,
            },
        },
    }


async def test_update_namespace_name(
    client: AsyncClient,
    access_token: str,
    user: User,
    namespace: Namespace,
    new_namespace: Namespace,
    session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await client.patch(
        f"v1/namespaces/{namespace.name}",
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

    changed_at = datetime.fromisoformat(content["changed_at"])
    assert changed_at >= current_dt >= namespace.changed_at

    query = select(Namespace).where(Namespace.id == namespace.id)
    query_result = await session.scalars(query)
    namespace_after = query_result.one()

    # Row is same as in body
    assert namespace_after.name == content["name"]
    assert namespace_after.description == content["description"]
    assert namespace_after.changed_at == changed_at
    assert namespace_after.changed_by_user_id == user.id
    assert not namespace_after.is_deleted


async def test_update_namespace_description(
    client: AsyncClient,
    access_token: str,
    user: User,
    namespace: Namespace,
    new_namespace: Namespace,
    session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)
    response = await client.patch(
        f"v1/namespaces/{namespace.name}",
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

    changed_at = datetime.fromisoformat(content["changed_at"])
    assert changed_at >= current_dt >= namespace.changed_at

    query = select(Namespace).where(Namespace.id == namespace.id)
    query_result = await session.scalars(query)
    namespace_after = query_result.one()

    # Row is same as in body
    assert namespace_after.name == content["name"]
    assert namespace_after.description == content["description"]
    assert namespace_after.changed_at == changed_at
    assert namespace_after.changed_by_user_id == user.id
    assert not namespace_after.is_deleted


async def test_update_namespace_duplicated_name(
    client: AsyncClient,
    access_token: str,
    namespaces: list[Namespace],
    session: AsyncSession,
):
    namespace1, namespace2, *_ = namespaces

    response = await client.patch(
        f"v1/namespaces/{namespace1.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": namespace2.name,
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "already_exists",
            "message": f"Namespace with name='{namespace2.name}' already exists",
            "details": {
                "entity_type": "Namespace",
                "field": "name",
                "value": namespace2.name,
            },
        },
    }

    query = select(Namespace).where(Namespace.id == namespace1.id)
    query_result = await session.scalars(query)
    namespace1_after = query_result.one()

    # Nothing is changed
    assert naturally_equivalent(namespace1_after, namespace1)

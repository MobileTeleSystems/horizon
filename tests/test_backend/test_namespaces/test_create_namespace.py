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


async def test_create_namespace_anonymous_user(
    client: AsyncClient,
):
    response = await client.post(
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
        },
    }


async def test_create_namespace(
    client: AsyncClient,
    access_token: str,
    user: User,
    new_namespace: Namespace,
    session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await client.post(
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

    changed_at = datetime.fromisoformat(content["changed_at"])
    assert changed_at >= current_dt

    query = select(Namespace).where(Namespace.id == namespace_id)
    query_result = await session.scalars(query)
    created_namespace = query_result.one()

    # Row is same as in body
    assert created_namespace.name == content["name"]
    assert created_namespace.description == content["description"]
    assert created_namespace.changed_at == changed_at
    assert created_namespace.changed_by_user_id == user.id
    assert not created_namespace.is_deleted


async def test_create_namespace_duplicated_name(
    client: AsyncClient,
    access_token: str,
    namespace: Namespace,
    session: AsyncSession,
):
    response = await client.post(
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
            "message": f"Namespace with name='{namespace.name}' already exists",
            "details": {
                "entity_type": "Namespace",
                "field": "name",
                "value": namespace.name,
            },
        },
    }

    query = select(Namespace).where(Namespace.id == namespace.id)
    query_result = await session.scalars(query)
    namespace_after = query_result.one()

    # Nothing is changed
    assert naturally_equivalent(namespace_after, namespace)

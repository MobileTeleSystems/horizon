# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from horizon.backend.db.models import Namespace

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.asyncio]


async def test_get_namespace_anonymous_user(
    test_client: AsyncClient,
    namespace: Namespace,
):
    response = await test_client.get(
        f"v1/namespaces/{namespace.name}",
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
        },
    }


async def test_get_namespace_missing(
    test_client: AsyncClient,
    access_token: str,
    new_namespace: Namespace,
):
    response = await test_client.get(
        f"v1/namespaces/{new_namespace.name}",
        headers={"Authorization": f"Bearer {access_token}"},
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


async def test_get_namespace(
    test_client: AsyncClient,
    access_token: str,
    namespace: Namespace,
    async_session: AsyncSession,
):
    query = select(Namespace).where(Namespace.id == namespace.id)
    query_result = await async_session.scalars(query)
    real_namespace = query_result.one()

    response = await test_client.get(
        f"v1/namespaces/{namespace.name}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": real_namespace.id,
        "name": real_namespace.name,
        "description": real_namespace.description,
        "changed_at": real_namespace.changed_at.isoformat(),
        "changed_by": real_namespace.changed_by_user.username,
    }

from __future__ import annotations

from datetime import datetime
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from horizon.backend.db.models import Namespace

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_get_namespace_anonymous_user(
    test_client: AsyncClient,
    namespace: Namespace,
):
    response = await test_client.get(
        f"v1/namespaces/{namespace.id}",
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_get_namespace_missing(
    test_client: AsyncClient,
    access_token: str,
    new_namespace: Namespace,
):
    response = await test_client.get(
        f"v1/namespaces/{new_namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
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
        f"v1/namespaces/{namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == HTTPStatus.OK

    response_dict = response.json()
    response_dict["changed_at"] = datetime.fromisoformat(response_dict["changed_at"].replace("Z", "+00:00"))
    assert response_dict == {
        "id": real_namespace.id,
        "name": real_namespace.name,
        "description": real_namespace.description,
        "changed_at": real_namespace.changed_at,
        "changed_by": real_namespace.changed_by_user.username,
        "owned_by": real_namespace.owner.username,
    }

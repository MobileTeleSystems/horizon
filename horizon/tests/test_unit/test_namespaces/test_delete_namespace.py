from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from app.db.models import Namespace, User

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.asyncio]


async def test_delete_namespace_anonymous_user(
    client: AsyncClient,
    namespace: Namespace,
):
    response = await client.delete(
        f"v1/namespaces/{namespace.name}",
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
        },
    }


async def test_delete_namespace_missing(
    client: AsyncClient,
    access_token: str,
    new_namespace: Namespace,
):
    response = await client.delete(
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


async def test_delete_namespace(
    client: AsyncClient,
    access_token: str,
    user: User,
    namespace: Namespace,
    session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await client.delete(
        f"v1/namespaces/{namespace.name}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204
    assert not response.content

    query = select(Namespace).where(Namespace.id == namespace.id)
    query_result = await session.scalars(query)
    namespace_after = query_result.one()

    # Field values are left intact
    assert namespace_after.name == namespace.name
    assert namespace_after.description == namespace.description
    # Internal fields are updated
    assert namespace_after.changed_at >= current_dt >= namespace.changed_at
    assert namespace_after.changed_by_user_id == user.id
    assert namespace_after.is_deleted

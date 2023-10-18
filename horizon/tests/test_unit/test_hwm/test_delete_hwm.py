from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select
from sqlalchemy_utils.functions import naturally_equivalent

from app.db.models import HWM, Namespace, User

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.asyncio]


async def test_delete_hwm_anonymous_user(
    client: AsyncClient,
    namespace: Namespace,
    new_hwm: HWM,
):
    response = await client.delete(
        f"v1/namespaces/{namespace.name}/hwm/{new_hwm.name}",
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
        },
    }


async def test_delete_hwm_missing_namespace(
    client: AsyncClient,
    new_namespace: Namespace,
    access_token: str,
    new_hwm: HWM,
):
    response = await client.delete(
        f"v1/namespaces/{new_namespace.name}/hwm/{new_hwm.name}",
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


async def test_delete_hwm_missing_hwm(
    client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    new_hwm: HWM,
):
    response = await client.delete(
        f"v1/namespaces/{namespace.name}/hwm/{new_hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"HWM with name='{new_hwm.name}' not found",
            "details": {
                "entity_type": "HWM",
                "field": "name",
                "value": new_hwm.name,
            },
        },
    }


async def test_delete_hwm(
    client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    user: User,
    hwm: HWM,
    session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await client.delete(
        f"v1/namespaces/{namespace.name}/hwm/{hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204
    assert not response.content

    query = select(HWM).where(HWM.id == hwm.id)
    query_result = await session.scalars(query)
    hwm_after = query_result.one()

    # Field values are left intact
    assert hwm_after.name == hwm.name
    assert hwm_after.description == hwm.description
    assert hwm_after.type == hwm.type
    assert hwm_after.value == hwm.value
    assert hwm_after.entity == hwm.entity
    assert hwm_after.expression == hwm.expression
    # Internal fields are updated
    assert hwm_after.changed_at >= current_dt
    assert naturally_equivalent(hwm_after.changed_by_user, user)
    assert hwm_after.is_deleted

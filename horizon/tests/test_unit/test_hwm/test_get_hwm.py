from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from app.db.models import HWM, Namespace

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.asyncio]


async def test_get_hwm_anonymous_user(
    client: AsyncClient,
    namespace: Namespace,
    hwm: HWM,
):
    response = await client.get(
        f"v1/namespaces/{namespace.name}/hwm/{hwm.name}",
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
        },
    }


async def test_get_hwm_missing_namespace(
    client: AsyncClient,
    new_namespace: Namespace,
    access_token: str,
    new_hwm: HWM,
):
    response = await client.get(
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


async def test_get_hwm_missing_hwm(
    client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    new_hwm: HWM,
):
    response = await client.get(
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


async def test_get_hwm(
    client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    hwm: HWM,
    session: AsyncSession,
):
    query = select(HWM).where(HWM.id == hwm.id)
    query_result = await session.scalars(query)
    real_hwm = query_result.one()

    response = await client.get(
        f"v1/namespaces/{namespace.name}/hwm/{hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "id": real_hwm.id,
        "name": real_hwm.name,
        "description": real_hwm.description,
        "type": real_hwm.type,
        "value": real_hwm.value,
        "entity": real_hwm.entity,
        "expression": real_hwm.expression,
        "changed_at": real_hwm.changed_at.isoformat(),
        "changed_by": real_hwm.changed_by_user.username,
    }

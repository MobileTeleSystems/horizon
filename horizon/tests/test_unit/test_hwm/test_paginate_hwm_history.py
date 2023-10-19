from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from app.db.models import HWM, HWMHistory, Namespace

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.asyncio]


async def test_paginate_hwm_history_anonymous_user(
    client: AsyncClient,
    namespace: Namespace,
    hwm: HWM,
):
    response = await client.get(f"v1/namespaces/{namespace.name}/hwm/{hwm.name}/history")
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
        },
    }


async def test_paginate_hwm_history_missing_namespace(
    client: AsyncClient,
    new_namespace: Namespace,
    new_hwm: HWM,
    access_token: str,
):
    response = await client.get(
        f"v1/namespaces/{new_namespace.name}/hwm/{new_hwm.name}/history",
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


async def test_paginate_hwm_history_missing_hwm(
    client: AsyncClient,
    namespace: Namespace,
    new_hwm: HWM,
    access_token: str,
):
    response = await client.get(
        f"v1/namespaces/{namespace.name}/hwm/{new_hwm.name}/history",
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


async def test_paginate_hwm_history_empty(
    client: AsyncClient,
    namespace: Namespace,
    hwm: HWM,
    access_token: str,
):
    response = await client.get(
        f"v1/namespaces/{namespace.name}/hwm/{hwm.name}/history",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "meta": {
            "page": 1,
            "pages_count": 1,
            "page_size": 20,
            "total_count": 0,
            "has_next": False,
            "has_previous": False,
            "next_page": None,
            "previous_page": None,
        },
        "items": [],
    }


async def test_paginate_hwm_history(
    client: AsyncClient,
    namespace: Namespace,
    hwm: HWM,
    access_token: str,
    hwm_history_items: list[HWMHistory],
):
    response = await client.get(
        f"v1/namespaces/{namespace.name}/hwm/{hwm.name}/history",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    items = [
        {
            "id": item.id,
            "hwm_id": item.hwm_id,
            "name": item.name,
            "description": item.description,
            "type": item.type,
            "value": item.value,
            "entity": item.entity,
            "expression": item.expression,
            "changed_at": item.changed_at.isoformat(),
            "changed_by": item.changed_by,
        }
        for item in sorted(hwm_history_items, key=lambda ns: ns.changed_at, reverse=True)
    ]

    assert response.json() == {
        "meta": {
            "page": 1,
            "pages_count": 1,
            "page_size": 20,
            "total_count": len(items),
            "has_next": False,
            "has_previous": False,
            "next_page": None,
            "previous_page": None,
        },
        "items": items,
    }

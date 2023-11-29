# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest

from horizon.backend.db.models import HWM, HWMHistory, Namespace

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_paginate_hwm_history_anonymous_user(
    test_client: AsyncClient,
    namespace: Namespace,
    hwm: HWM,
):
    response = await test_client.get(f"v1/namespaces/{namespace.name}/hwm/{hwm.name}/history")
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_paginate_hwm_history_missing_namespace(
    test_client: AsyncClient,
    new_namespace: Namespace,
    new_hwm: HWM,
    access_token: str,
):
    response = await test_client.get(
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
    test_client: AsyncClient,
    namespace: Namespace,
    new_hwm: HWM,
    access_token: str,
):
    response = await test_client.get(
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
    test_client: AsyncClient,
    namespace: Namespace,
    hwm: HWM,
    access_token: str,
):
    response = await test_client.get(
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
    test_client: AsyncClient,
    namespace: Namespace,
    hwm: HWM,
    access_token: str,
    hwm_history_items: list[HWMHistory],
):
    hwm_history_items = sorted(hwm_history_items, key=lambda ns: ns.changed_at, reverse=True)

    response = await test_client.get(
        f"v1/namespaces/{namespace.name}/hwm/{hwm.name}/history",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict.keys() == {"meta", "items"}
    assert response_dict["meta"] == {
        "page": 1,
        "pages_count": 1,
        "page_size": 20,
        "total_count": len(hwm_history_items),
        "has_next": False,
        "has_previous": False,
        "next_page": None,
        "previous_page": None,
    }

    response_items = response_dict["items"]

    for i, hwm_history_item in enumerate(hwm_history_items):
        response_item = response_items[i]
        response_item["changed_at"] = datetime.fromisoformat(response_item["changed_at"].replace("Z", "+00:00"))

        assert response_item == {
            "id": hwm_history_item.id,
            "hwm_id": hwm_history_item.hwm_id,
            "name": hwm_history_item.name,
            "description": hwm_history_item.description,
            "type": hwm_history_item.type,
            "value": hwm_history_item.value,
            "entity": hwm_history_item.entity,
            "expression": hwm_history_item.expression,
            "changed_at": hwm_history_item.changed_at,
            "changed_by": hwm_history_item.changed_by,
        }

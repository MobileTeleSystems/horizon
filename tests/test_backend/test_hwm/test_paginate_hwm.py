# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest

from horizon.backend.db.models import HWM, Namespace

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_paginate_hwm_anonymous_user(
    test_client: AsyncClient,
    namespace: Namespace,
):
    response = await test_client.get(f"v1/namespaces/{namespace.name}/hwm/")
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_paginate_hwm_missing_namespace(
    test_client: AsyncClient,
    new_namespace: Namespace,
    access_token: str,
):
    response = await test_client.get(
        f"v1/namespaces/{new_namespace.name}/hwm/",
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


async def test_paginate_hwm_empty(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
):
    response = await test_client.get(
        f"v1/namespaces/{namespace.name}/hwm/",
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


async def test_paginate_hwm(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    hwms: list[HWM],
):
    hwms = sorted(hwms, key=lambda ns: ns.name)

    response = await test_client.get(
        f"v1/namespaces/{namespace.name}/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict.keys() == {"meta", "items"}
    assert response_dict["meta"] == {
        "page": 1,
        "pages_count": 1,
        "page_size": 20,
        "total_count": len(hwms),
        "has_next": False,
        "has_previous": False,
        "next_page": None,
        "previous_page": None,
    }

    response_items = response_dict["items"]

    for i, hwm in enumerate(hwms):
        response_item = response_items[i]
        response_item["changed_at"] = datetime.fromisoformat(response_item["changed_at"].replace("Z", "+00:00"))

        assert response_item == {
            "id": hwm.id,
            "name": hwm.name,
            "description": hwm.description,
            "type": hwm.type,
            "value": hwm.value,
            "entity": hwm.entity,
            "expression": hwm.expression,
            "changed_at": hwm.changed_at,
            "changed_by": hwm.changed_by,
        }


@pytest.mark.parametrize("hwm", [{"is_deleted": True}], indirect=True)
async def test_paginate_hwm_deleted_not_included(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    hwm: HWM,
):
    response = await test_client.get(
        f"v1/namespaces/{namespace.name}/hwm/",
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

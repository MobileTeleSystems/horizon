# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import __version__ as pydantic_version

from horizon.backend.db.models import HWM, HWMHistory

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_paginate_hwm_history_anonymous_user(
    test_client: AsyncClient,
    hwm: HWM,
):
    response = await test_client.get(
        "v1/hwm-history/",
        params={"hwm_id": hwm.id},
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_paginate_hwm_history_not_enough_arguments(
    test_client: AsyncClient,
    access_token: str,
):
    response = await test_client.get(
        "v1/hwm-history/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    details: list[dict[str, Any]]
    if pydantic_version < "2":
        details = [
            {
                "location": ["query", "hwm_id"],
                "code": "value_error.missing",
                "message": "field required",
            },
        ]
    else:
        details = [
            {
                "code": "missing",
                "context": {},
                "input": None,
                "location": ["query", "hwm_id"],
                "message": "Field required",
            },
        ]

    assert response.json() == {
        "error": {
            "code": "invalid_request",
            "message": "Invalid request",
            "details": details,
        },
    }


async def test_paginate_hwm_history_missing_hwm(
    test_client: AsyncClient,
    new_hwm: HWM,
    access_token: str,
):
    response = await test_client.get(
        "v1/hwm-history/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"hwm_id": new_hwm.id},
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


async def test_paginate_hwm_history_empty_hwm_history(
    test_client: AsyncClient,
    hwm: HWM,
    access_token: str,
):
    response = await test_client.get(
        "v1/hwm-history/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"hwm_id": hwm.id},
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
    hwm: HWM,
    access_token: str,
    hwm_history_items: list[HWMHistory],
):
    hwm_history_items = sorted(hwm_history_items, key=lambda ns: ns.changed_at, reverse=True)

    response = await test_client.get(
        "v1/hwm-history/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"hwm_id": hwm.id},
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
            "namespace_id": hwm_history_item.namespace_id,
            "name": hwm_history_item.name,
            "description": hwm_history_item.description,
            "type": hwm_history_item.type,
            "value": hwm_history_item.value,
            "entity": hwm_history_item.entity,
            "expression": hwm_history_item.expression,
            "action": hwm_history_item.action,
            "changed_at": hwm_history_item.changed_at,
            "changed_by": hwm_history_item.changed_by,
        }

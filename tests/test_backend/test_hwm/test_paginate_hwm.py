from __future__ import annotations

from copy import copy
from datetime import datetime
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import __version__ as pydantic_version

from horizon.backend.db.models import HWM, Namespace

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_paginate_hwm_anonymous_user(
    test_client: AsyncClient,
    new_namespace: Namespace,
):
    response = await test_client.get(
        "v1/hwm/",
        params={"namespace_id": new_namespace.id},
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_paginate_hwm_not_enough_arguments(
    test_client: AsyncClient,
    access_token: str,
):
    response = await test_client.get(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 422

    details: list[dict[str, Any]]
    if pydantic_version < "2":
        details = [
            {
                "location": ["query", "namespace_id"],
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
                "location": ["query", "namespace_id"],
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


async def test_paginate_hwm_missing_namespace(
    test_client: AsyncClient,
    new_namespace: Namespace,
    access_token: str,
):
    response = await test_client.get(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"namespace_id": new_namespace.id},
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


async def test_paginate_hwm_empty_namespace(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
):
    response = await test_client.get(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"namespace_id": namespace.id},
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
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"namespace_id": namespace.id},
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
        response_item = copy(response_items[i])
        response_item["changed_at"] = datetime.fromisoformat(response_item["changed_at"].replace("Z", "+00:00"))

        assert response_item == {
            "id": hwm.id,
            "namespace_id": hwm.namespace_id,
            "name": hwm.name,
            "description": hwm.description,
            "type": hwm.type,
            "value": hwm.value,
            "entity": hwm.entity,
            "expression": hwm.expression,
            "changed_at": hwm.changed_at,
            "changed_by": hwm.changed_by,
        }


async def test_paginate_hwm_filter_by_name(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    hwms: list[HWM],
):
    hwm = hwms[0]

    response = await test_client.get(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"namespace_id": namespace.id, "name": hwm.name},
    )
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict.keys() == {"meta", "items"}
    assert response_dict["meta"] == {
        "page": 1,
        "pages_count": 1,
        "page_size": 20,
        "total_count": 1,
        "has_next": False,
        "has_previous": False,
        "next_page": None,
        "previous_page": None,
    }

    response_items = response_dict["items"]
    for response_item in response_items:
        response_item["changed_at"] = datetime.fromisoformat(response_item["changed_at"].replace("Z", "+00:00"))

    assert response_dict["items"] == [
        {
            "id": hwm.id,
            "namespace_id": hwm.namespace_id,
            "name": hwm.name,
            "description": hwm.description,
            "type": hwm.type,
            "value": hwm.value,
            "entity": hwm.entity,
            "expression": hwm.expression,
            "changed_at": hwm.changed_at,
            "changed_by": hwm.changed_by,
        },
    ]


async def test_paginate_hwm_filter_by_missing_name(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    new_hwm: HWM,
):
    response = await test_client.get(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        params={"namespace_id": namespace.id, "name": new_hwm.name},
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

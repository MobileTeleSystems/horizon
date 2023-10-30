# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.db.models import HWM, Namespace

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.asyncio]


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
    response = await test_client.get(
        f"v1/namespaces/{namespace.name}/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    items = [
        {
            "id": hwm.id,
            "name": hwm.name,
            "description": hwm.description,
            "type": hwm.type,
            "value": hwm.value,
            "entity": hwm.entity,
            "expression": hwm.expression,
            "changed_at": hwm.changed_at.isoformat(),
            "changed_by": hwm.changed_by,
        }
        for hwm in sorted(hwms, key=lambda ns: ns.name)
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

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest

from horizon.backend.db.models import Namespace

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.asyncio]


async def test_paginate_namespaces_anonymous_user(
    test_client: AsyncClient,
):
    response = await test_client.get("v1/namespaces/")
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_paginate_namespaces_empty(
    test_client: AsyncClient,
    access_token: str,
):
    response = await test_client.get(
        "v1/namespaces/",
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


async def test_paginate_namespaces(
    test_client: AsyncClient,
    access_token: str,
    namespaces: list[Namespace],
):
    namespaces = sorted(namespaces, key=lambda ns: ns.name)

    response = await test_client.get(
        "v1/namespaces/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    response_dict = response.json()
    assert response_dict.keys() == {"meta", "items"}
    assert response_dict["meta"] == {
        "page": 1,
        "pages_count": 1,
        "page_size": 20,
        "total_count": len(namespaces),
        "has_next": False,
        "has_previous": False,
        "next_page": None,
        "previous_page": None,
    }

    response_items = response_dict["items"]

    for i, namespace in enumerate(namespaces):
        response_item = response_items[i]
        response_item["changed_at"] = datetime.fromisoformat(response_item["changed_at"].replace("Z", "+00:00"))

        assert response_item == {
            "id": namespace.id,
            "name": namespace.name,
            "description": namespace.description,
            "changed_at": namespace.changed_at,
            "changed_by": namespace.changed_by,
        }


@pytest.mark.parametrize("namespace", [{"is_deleted": True}], indirect=True)
async def test_paginate_namespaces_deleted_not_included(
    test_client: AsyncClient,
    access_token: str,
    namespace: Namespace,
):
    response = await test_client.get(
        "v1/namespaces/",
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

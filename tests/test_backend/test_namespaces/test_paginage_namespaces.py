# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.db.models import Namespace

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.asyncio]


async def test_paginate_namespaces_anonymous_user(
    client: AsyncClient,
):
    response = await client.get("v1/namespaces/")
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
        },
    }


async def test_paginate_namespaces_empty(
    client: AsyncClient,
    access_token: str,
):
    response = await client.get(
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
    client: AsyncClient,
    access_token: str,
    namespaces: list[Namespace],
):
    response = await client.get(
        "v1/namespaces/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    items = [
        {
            "id": namespace.id,
            "name": namespace.name,
            "description": namespace.description,
            "changed_at": namespace.changed_at.isoformat(),
            "changed_by": namespace.changed_by,
        }
        for namespace in sorted(namespaces, key=lambda ns: ns.name)
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


@pytest.mark.parametrize("namespace", [{"is_deleted": True}], indirect=True)
async def test_paginate_namespaces_deleted_not_included(
    client: AsyncClient,
    access_token: str,
    namespace: Namespace,
):
    response = await client.get(
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

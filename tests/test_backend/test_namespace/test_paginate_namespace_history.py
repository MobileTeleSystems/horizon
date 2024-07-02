# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from copy import copy
from datetime import datetime
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import __version__ as pydantic_version

from horizon.backend.db.models import Namespace, NamespaceHistory

if TYPE_CHECKING:
    from httpx import AsyncClient

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_paginate_namespace_history_anonymous_user(
    test_client: AsyncClient,
    namespace: Namespace,
):
    response = await test_client.get(
        "v1/namespace-history/",
        params={"namespace_id": namespace.id},
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_paginate_namespace_history_not_enough_arguments(
    test_client: AsyncClient,
    access_token: str,
):
    response = await test_client.get(
        "v1/namespace-history/",
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


async def test_paginate_namespace_history_missing_namespace(
    test_client: AsyncClient,
    new_namespace: Namespace,
    access_token: str,
):
    response = await test_client.get(
        "v1/namespace-history/",
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


async def test_paginate_namespace_history_empty_namespace_history(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
):
    response = await test_client.get(
        "v1/namespace-history/",
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


async def test_paginate_namespace_history(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    namespace_history_items: list[NamespaceHistory],
):
    namespace_history_items = sorted(namespace_history_items, key=lambda ns: ns.changed_at, reverse=True)

    response = await test_client.get(
        "v1/namespace-history/",
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
        "total_count": len(namespace_history_items),
        "has_next": False,
        "has_previous": False,
        "next_page": None,
        "previous_page": None,
    }

    response_items = response_dict["items"]

    for i, namespace_history_item in enumerate(namespace_history_items):
        response_item = copy(response_items[i])
        response_item["changed_at"] = datetime.fromisoformat(response_item["changed_at"].replace("Z", "+00:00"))

        assert response_item == {
            "id": namespace_history_item.id,
            "namespace_id": namespace_history_item.namespace_id,
            "name": namespace_history_item.name,
            "description": namespace_history_item.description,
            "action": namespace_history_item.action,
            "changed_at": namespace_history_item.changed_at,
            "changed_by": namespace_history_item.changed_by,
            "owned_by": namespace_history_item.owned_by,
        }

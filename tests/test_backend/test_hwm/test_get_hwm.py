# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from horizon.backend.db.models import HWM, Namespace

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_get_hwm_anonymous_user(
    test_client: AsyncClient,
    hwm: HWM,
):
    response = await test_client.get(
        f"v1/hwm/{hwm.id}",
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_get_hwm_missing_hwm(
    test_client: AsyncClient,
    access_token: str,
    new_hwm: HWM,
):
    response = await test_client.get(
        f"v1/hwm/{new_hwm.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"HWM with id={new_hwm.id!r} not found",
            "details": {
                "entity_type": "HWM",
                "field": "id",
                "value": new_hwm.id,
            },
        },
    }


async def test_get_hwm(
    test_client: AsyncClient,
    access_token: str,
    hwm: HWM,
    async_session: AsyncSession,
):
    query = select(HWM).where(HWM.id == hwm.id)
    query_result = await async_session.scalars(query)
    real_hwm = query_result.one()

    response = await test_client.get(
        f"v1/hwm/{hwm.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200

    response_dict = response.json()
    response_dict["changed_at"] = datetime.fromisoformat(response_dict["changed_at"].replace("Z", "+00:00"))
    assert response_dict == {
        "id": real_hwm.id,
        "namespace_id": real_hwm.namespace_id,
        "name": real_hwm.name,
        "description": real_hwm.description,
        "type": real_hwm.type,
        "value": real_hwm.value,
        "entity": real_hwm.entity,
        "expression": real_hwm.expression,
        "changed_at": real_hwm.changed_at,
        "changed_by": real_hwm.changed_by_user.username,
    }

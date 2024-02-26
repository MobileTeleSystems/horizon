# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from horizon.backend.db.models import HWM, User
from horizon.backend.db.models.hwm_history import HWMHistory

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_delete_hwm_anonymous_user(
    test_client: AsyncClient,
    new_hwm: HWM,
):
    response = await test_client.delete(
        f"v1/hwm/{new_hwm.id}",
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_delete_hwm_missing(
    test_client: AsyncClient,
    access_token: str,
    new_hwm: HWM,
):
    response = await test_client.delete(
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


async def test_delete_hwm(
    test_client: AsyncClient,
    access_token: str,
    user: User,
    hwm: HWM,
    async_session: AsyncSession,
):
    pre_delete_timestamp = datetime.now(timezone.utc) - timedelta(minutes=1)
    response = await test_client.delete(
        f"v1/hwm/{hwm.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    post_delete_timestamp = datetime.now(timezone.utc)

    assert response.status_code == 204
    assert not response.content

    query = select(HWM).where(HWM.id == hwm.id)
    result = await async_session.execute(query)
    hwm_records = result.scalars().all()
    assert len(hwm_records) == 0

    query_history = select(HWMHistory).where(HWMHistory.hwm_id == hwm.id)
    result_history = await async_session.execute(query_history)
    created_hwm_history = result_history.scalars().one()

    assert created_hwm_history.name == hwm.name
    assert created_hwm_history.namespace_id == hwm.namespace_id
    assert created_hwm_history.description == hwm.description
    assert created_hwm_history.type == hwm.type
    assert created_hwm_history.value == hwm.value
    assert created_hwm_history.entity == hwm.entity
    assert created_hwm_history.expression == hwm.expression
    assert created_hwm_history.action == "Deleted"
    assert created_hwm_history.changed_by_user_id == user.id
    assert pre_delete_timestamp <= created_hwm_history.changed_at <= post_delete_timestamp

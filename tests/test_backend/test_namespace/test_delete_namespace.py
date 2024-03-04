# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from horizon.backend.db.models import HWM, Namespace, NamespaceHistory, User

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_delete_namespace_anonymous_user(
    test_client: AsyncClient,
    namespace: Namespace,
):
    response = await test_client.delete(
        f"v1/namespaces/{namespace.id}",
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_delete_namespace_missing(
    test_client: AsyncClient,
    access_token: str,
    new_namespace: Namespace,
):
    response = await test_client.delete(
        f"v1/namespaces/{new_namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"Namespace with owner_id={new_namespace.owner_id!r} not found",
            "details": {
                "entity_type": "Namespace",
                "field": "owner_id",
                "value": new_namespace.owner_id,
            },
        },
    }


async def test_delete_namespace(
    test_client: AsyncClient,
    access_token: str,
    user: User,
    namespace: Namespace,
    async_session: AsyncSession,
):
    pre_delete_timestamp = datetime.now(timezone.utc) - timedelta(minutes=1)
    response = await test_client.delete(
        f"v1/namespaces/{namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    post_delete_timestamp = datetime.now(timezone.utc)

    assert response.status_code == 204
    assert not response.content

    query = select(Namespace).where(Namespace.id == namespace.id)
    result = await async_session.execute(query)
    namespace_records = result.scalars().all()
    assert len(namespace_records) == 0

    query_history = select(NamespaceHistory).where(NamespaceHistory.namespace_id == namespace.id)
    result_history = await async_session.execute(query_history)
    created_namespace_history = result_history.scalars().one()

    assert created_namespace_history.name == namespace.name
    assert created_namespace_history.namespace_id == namespace.id
    assert created_namespace_history.description == namespace.description
    assert created_namespace_history.action == "Deleted"
    assert created_namespace_history.changed_by_user_id == user.id
    assert created_namespace_history.owner_id == user.id
    assert pre_delete_timestamp <= created_namespace_history.changed_at <= post_delete_timestamp


async def test_delete_namespace_with_existing_hwm(
    test_client: AsyncClient,
    access_token: str,
    user: User,
    namespace: Namespace,
    hwm: HWM,
    async_session: AsyncSession,
):
    response = await test_client.delete(
        f"v1/namespaces/{namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "error": {
            "code": "bad_request",
            "message": "Cannot delete namespace because it has related HWM records.",
            "details": None,
        },
    }

    query = select(Namespace).where(Namespace.id == namespace.id)
    result = await async_session.execute(query)
    namespace_record = result.scalars().first()
    assert namespace_record is not None

    query_hwm = select(HWM).where(HWM.namespace_id == namespace.id)
    result_hwm = await async_session.execute(query_hwm)
    hwm_records = result_hwm.scalars().all()
    assert len(hwm_records) > 0

    response = await test_client.delete(
        f"v1/hwm/{hwm.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 204

    response = await test_client.delete(
        f"v1/namespaces/{namespace.id}",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 204

    query = select(Namespace).where(Namespace.id == namespace.id)
    result = await async_session.execute(query)
    namespace_record = result.scalars().first()
    assert namespace_record is None

    query_hwm = select(HWM).where(HWM.namespace_id == namespace.id)
    result_hwm = await async_session.execute(query_hwm)
    hwm_records = result_hwm.scalars().all()
    assert len(hwm_records) == 0

# SPDX-FileCopyrightText: 2023 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from pydantic import __version__ as pydantic_version
from sqlalchemy import select

from horizon.backend.db.models import HWM, Namespace, NamespaceUserRoleInt
from horizon.backend.db.models.hwm_history import HWMHistory

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


@pytest.mark.parametrize("namespaces", [(2, {})], indirect=True)
async def test_copy_hwms_anonymous_user(
    test_client: AsyncClient,
    namespaces: list[Namespace],
    hwms: list[HWM],
):
    source_namespace, target_namespace = namespaces
    response = await test_client.post(
        "v1/hwm/copy",
        json={
            "source_namespace_id": source_namespace.id,
            "target_namespace_id": target_namespace.id,
            "hwm_ids": [hwm.id for hwm in hwms],
            "with_history": False,
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Not authenticated",
            "details": None,
        },
    }


async def test_copy_hwms_same_source_and_target_namespace(
    test_client: AsyncClient,
    access_token: str,
    namespace: Namespace,
    hwms: list[HWM],
):
    body = {
        "source_namespace_id": namespace.id,
        "target_namespace_id": namespace.id,
        "hwm_ids": [hwm.id for hwm in hwms],
        "with_history": False,
    }

    response = await test_client.post(
        "v1/hwm/copy",
        headers={"Authorization": f"Bearer {access_token}"},
        json=body,
    )

    assert response.status_code == 422

    if pydantic_version >= "2":
        detail = {
            "code": "value_error",
            "context": {},
            "input": body,
            "location": ["body"],
            "message": "Value error, Source and target namespace IDs must not be the same.",
        }
    else:
        detail = {
            "code": "value_error",
            "location": ["body", "__root__"],
            "message": "Source and target namespace IDs must not be the same.",
        }

    expected_body = {
        "error": {
            "code": "invalid_request",
            "details": [detail],
            "message": "Invalid request",
        },
    }

    assert response.json() == expected_body


@pytest.mark.asyncio
@pytest.mark.parametrize("with_history", [True, False])
async def test_copy_hwms(
    test_client: AsyncClient,
    access_token: str,
    namespaces: list[Namespace],
    hwms: list[HWM],
    hwm_history_items_for_hwms: list[HWMHistory],
    async_session: AsyncSession,
    with_history: bool,
):
    source_namespace = hwms[0].namespace
    target_namespace = namespaces[0]

    response = await test_client.post(
        "v1/hwm/copy",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "source_namespace_id": source_namespace.id,
            "target_namespace_id": target_namespace.id,
            "hwm_ids": [hwm.id for hwm in hwms],
            "with_history": with_history,
        },
    )

    assert response.status_code == 201

    for original_hwm in hwms:
        query = select(HWM).where(HWM.namespace_id == target_namespace.id, HWM.name == original_hwm.name)
        result = await async_session.execute(query)
        copied_hwm = result.scalars().first()
        assert copied_hwm is not None

        assert copied_hwm.name == original_hwm.name
        assert copied_hwm.description == original_hwm.description

        history_query = (
            select(HWMHistory).where(HWMHistory.hwm_id == copied_hwm.id).order_by(HWMHistory.changed_at.desc())
        )
        history_result = await async_session.execute(history_query)
        copied_history_records = history_result.scalars().all()

        original_history_query = (
            select(HWMHistory).where(HWMHistory.hwm_id == original_hwm.id).order_by(HWMHistory.changed_at.desc())
        )
        original_history_result = await async_session.execute(original_history_query)
        original_history_records = original_history_result.scalars().all()

        copied_action_record = copied_history_records[-1]
        assert copied_action_record is not None
        expected_action = f"Copied from namespace {source_namespace.id} to namespace {target_namespace.id}"
        assert copied_action_record.action == expected_action

        if with_history:
            assert len(copied_history_records) == len(original_history_records) + 1

            for original_record, copied_record in zip(original_history_records, copied_history_records[:-1]):
                assert original_record.name == copied_record.name
                assert original_record.description == copied_record.description
                assert original_record.type == copied_record.type
                assert original_record.value == copied_record.value
                assert original_record.entity == copied_record.entity
                assert original_record.expression == copied_record.expression
                assert copied_record.namespace_id == source_namespace.id


@pytest.mark.asyncio
async def test_copy_hwms_empty_hwm_ids_list(
    test_client: AsyncClient,
    access_token: str,
    namespaces: list[Namespace],
):
    source_namespace, target_namespace = namespaces[:2]
    response = await test_client.post(
        "v1/hwm/copy",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "source_namespace_id": source_namespace.id,
            "target_namespace_id": target_namespace.id,
            "hwm_ids": [],
            "with_history": False,
        },
    )

    assert response.status_code == 422

    if pydantic_version >= "2":
        detail = {
            "code": "value_error",
            "context": {},
            "input": [],
            "location": ["body", "hwm_ids"],
            "message": "Value error, List should have at least 1 item after validation, not 0",
        }
    else:
        detail = {
            "code": "value_error",
            "location": ["body", "hwm_ids"],
            "message": "List should have at least 1 item after validation, not 0",
        }

    expected_body = {
        "error": {
            "code": "invalid_request",
            "details": [detail],
            "message": "Invalid request",
        },
    }

    assert response.json() == expected_body


@pytest.mark.asyncio
async def test_copy_hwms_with_non_existing_hwm_ids(
    test_client: AsyncClient,
    access_token: str,
    namespaces: list[Namespace],
    new_hwm: HWM,
    async_session: AsyncSession,
):
    source_namespace, target_namespace = namespaces[:2]

    response = await test_client.post(
        "v1/hwm/copy",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "source_namespace_id": source_namespace.id,
            "target_namespace_id": target_namespace.id,
            "hwm_ids": [new_hwm.id],
            "with_history": False,
        },
    )
    # we ignore hwms that are not related to namespace and copy only existing hws in namespace
    assert response.status_code == 201
    assert response.json() == {"hwms": []}

    query = select(HWM).where(HWM.namespace_id == target_namespace.id, HWM.name == new_hwm.name)
    result = await async_session.execute(query)
    non_existing_copied_hwm = result.scalars().first()

    assert non_existing_copied_hwm is None


@pytest.mark.asyncio
@pytest.mark.parametrize("non_existing_namespace_position", ["source", "target"])
async def test_copy_hwms_non_existing_namespace(
    test_client: AsyncClient,
    access_token: str,
    namespace: Namespace,
    new_namespace: Namespace,
    hwms: list[HWM],
    non_existing_namespace_position: str,
):
    if non_existing_namespace_position == "source":
        source_namespace_id = new_namespace.id
        target_namespace_id = namespace.id
    else:
        source_namespace_id = namespace.id
        target_namespace_id = new_namespace.id

    response = await test_client.post(
        "v1/hwm/copy",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "source_namespace_id": source_namespace_id,
            "target_namespace_id": target_namespace_id,
            "hwm_ids": [hwm.id for hwm in hwms],
            "with_history": False,
        },
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"Namespace with id={new_namespace.id!r} not found",
            "details": {
                "entity_type": "Namespace",
                "field": "id",
                "value": new_namespace.id,
            },
        },
    }


@pytest.mark.asyncio
async def test_copy_hwms_with_existing_hwm_name(
    test_client: AsyncClient,
    access_token: str,
    namespaces: list[Namespace],
    hwms: list[HWM],
    async_session: AsyncSession,
):
    source_namespace = hwms[0].namespace
    target_namespace = namespaces[0]

    existing_hwm = hwms[0]
    existing_hwm_copy = HWM(
        namespace_id=target_namespace.id,
        name=existing_hwm.name,
        description=existing_hwm.description,
        type=existing_hwm.type,
        value=existing_hwm.value,
        entity=existing_hwm.entity,
        expression=existing_hwm.expression,
        changed_by_user_id=existing_hwm.changed_by_user_id,
    )
    async_session.add(existing_hwm_copy)
    await async_session.commit()

    response = await test_client.post(
        "v1/hwm/copy",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "source_namespace_id": source_namespace.id,
            "target_namespace_id": target_namespace.id,
            "hwm_ids": [hwm.id for hwm in hwms],
            "with_history": False,
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "already_exists",
            "details": {"entity_type": "HWM", "field": "name", "value": hwms[0].name},
            "message": f"HWM with name={hwms[0].name!r} already exists",
        },
    }


@pytest.mark.parametrize("namespaces", [(1, {})], indirect=True)
@pytest.mark.parametrize(
    "user_with_role, expected_status, expected_response",
    [
        (
            NamespaceUserRoleInt.GUEST,
            403,
            {
                "error": {
                    "code": "permission_denied",
                    "message": "Permission denied. User has role GUEST but action requires at least DEVELOPER.",
                    "details": {
                        "required_role": "DEVELOPER",
                        "actual_role": "GUEST",
                    },
                },
            },
        ),
    ],
    indirect=["user_with_role"],
)
async def test_copy_hwms_permission_denied(
    test_client: AsyncClient,
    access_token: str,
    user_with_role: None,
    namespaces: list[Namespace],
    namespace: Namespace,
    hwms: list[HWM],
    expected_response,
    expected_status,
):
    source_namespace = namespaces[0]
    response = await test_client.post(
        "v1/hwm/copy",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "source_namespace_id": source_namespace.id,
            "target_namespace_id": namespace.id,
            "hwm_ids": [hwm.id for hwm in hwms],
            "with_history": False,
        },
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response

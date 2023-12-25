# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import __version__ as pydantic_version
from sqlalchemy import select
from sqlalchemy_utils.functions import naturally_equivalent

from horizon.backend.db.models import HWM, HWMHistory, Namespace, User

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.backend, pytest.mark.asyncio]


async def test_create_hwm_anonymous_user(
    test_client: AsyncClient,
    namespace: Namespace,
    new_hwm: HWM,
):
    response = await test_client.post(
        "v1/hwm/",
        json={
            "namespace_id": namespace.id,
            "name": new_hwm.name,
            "description": new_hwm.description,
            "type": new_hwm.type,
            "value": new_hwm.value,
            "entity": new_hwm.entity,
            "expression": new_hwm.expression,
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


async def test_create_hwm_missing_namespace(
    test_client: AsyncClient,
    new_namespace: Namespace,
    access_token: str,
    new_hwm: HWM,
):
    response = await test_client.post(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "namespace_id": new_namespace.id,
            "name": new_hwm.name,
            "description": new_hwm.description,
            "type": new_hwm.type,
            "value": new_hwm.value,
            "entity": new_hwm.entity,
            "expression": new_hwm.expression,
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


@pytest.mark.parametrize(
    "new_hwm",
    [
        pytest.param({"name": "a" * 2048}, id="max-name"),
        pytest.param({"type": "a" * 64}, id="max-type"),
    ],
    indirect=True,
)
async def test_create_hwm(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    user: User,
    new_hwm: HWM,
    async_session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await test_client.post(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "namespace_id": namespace.id,
            "name": new_hwm.name,
            "description": new_hwm.description,
            "type": new_hwm.type,
            "value": new_hwm.value,
            "entity": new_hwm.entity,
            "expression": new_hwm.expression,
        },
    )
    assert response.status_code == 201

    content = response.json()
    hmw_id = content["id"]
    assert hmw_id
    assert content["name"] == new_hwm.name
    assert content["description"] == new_hwm.description
    assert content["type"] == new_hwm.type
    assert content["value"] == new_hwm.value
    assert content["entity"] == new_hwm.entity
    assert content["expression"] == new_hwm.expression
    assert content["changed_by"] == user.username

    changed_at = datetime.fromisoformat(content["changed_at"].replace("Z", "+00:00"))
    assert changed_at >= current_dt

    query = select(HWM).where(HWM.id == hmw_id)
    query_result = await async_session.scalars(query)
    created_hwm = query_result.one()

    # Row is same as in body
    assert created_hwm.name == content["name"]
    assert created_hwm.description == content["description"]
    assert created_hwm.type == content["type"]
    assert created_hwm.value == content["value"]
    assert created_hwm.entity == content["entity"]
    assert created_hwm.expression == content["expression"]
    assert created_hwm.changed_at == changed_at
    assert created_hwm.changed_by_user_id == user.id
    assert not created_hwm.is_deleted

    query = select(HWMHistory).where(HWMHistory.hwm_id == hmw_id)
    query_result = await async_session.scalars(query)
    created_hwm_history = query_result.one()

    # Row is same as in body
    assert created_hwm_history.name == content["name"]
    assert created_hwm_history.description == content["description"]
    assert created_hwm_history.type == content["type"]
    assert created_hwm_history.value == content["value"]
    assert created_hwm_history.entity == content["entity"]
    assert created_hwm_history.expression == content["expression"]
    assert created_hwm_history.changed_at == changed_at
    assert created_hwm_history.changed_by_user_id == user.id
    assert not created_hwm_history.is_deleted


async def test_create_hwm_only_mandatory_fields(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    user: User,
    new_hwm: HWM,
    async_session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await test_client.post(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "namespace_id": namespace.id,
            "name": new_hwm.name,
            "type": new_hwm.type,
            "value": None,
        },
    )
    assert response.status_code == 201

    content = response.json()
    hmw_id = content["id"]
    assert hmw_id
    assert content["name"] == new_hwm.name
    assert content["description"] == ""
    assert content["type"] == new_hwm.type
    assert content["value"] is None
    assert content["entity"] is None
    assert content["expression"] is None
    assert content["changed_by"] == user.username

    changed_at = datetime.fromisoformat(content["changed_at"].replace("Z", "+00:00"))
    assert changed_at >= current_dt

    query = select(HWM).where(HWM.id == hmw_id)
    query_result = await async_session.scalars(query)
    created_hwm = query_result.one()

    # Row is same as in body
    assert created_hwm.name == content["name"]
    assert created_hwm.description == content["description"]
    assert created_hwm.type == content["type"]
    assert created_hwm.value == content["value"]
    assert created_hwm.entity == content["entity"]
    assert created_hwm.expression == content["expression"]
    assert created_hwm.changed_at == changed_at
    assert created_hwm.changed_by_user_id == user.id
    assert not created_hwm.is_deleted


async def test_create_hwm_create_new_with_same_name_in_different_namespaces(
    test_client: AsyncClient,
    namespaces: list[Namespace],
    access_token: str,
    new_hwm: HWM,
    async_session: AsyncSession,
):
    namespace1, namespace2, *_ = namespaces

    response1 = await test_client.post(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "namespace_id": namespace1.id,
            "name": new_hwm.name,
            "type": "abc",
            "value": 123,
        },
    )
    assert response1.status_code == 201

    response2 = await test_client.post(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "namespace_id": namespace2.id,
            "name": new_hwm.name,
            "type": "bcd",
            "value": 234,
        },
    )
    assert response2.status_code == 201

    hmw1_id = response1.json()["id"]
    hmw2_id = response2.json()["id"]
    assert hmw1_id != hmw2_id

    query1 = select(HWM).where(HWM.id == hmw1_id)
    query_result1 = await async_session.scalars(query1)
    created_hwm1 = query_result1.one()

    query2 = select(HWM).where(HWM.id == hmw2_id)
    query_result2 = await async_session.scalars(query2)
    created_hwm2 = query_result2.one()

    assert created_hwm1.name == created_hwm2.name == new_hwm.name
    assert created_hwm1.type == "abc"
    assert created_hwm1.value == 123
    assert created_hwm2.type == "bcd"
    assert created_hwm2.value == 234


async def test_create_hwm_already_exist(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    hwm: HWM,
    new_hwm: HWM,
    async_session: AsyncSession,
):
    response = await test_client.post(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "namespace_id": namespace.id,
            "name": hwm.name,
            "description": new_hwm.description,
            "type": new_hwm.type,
            "value": new_hwm.value,
            "entity": new_hwm.entity,
            "expression": new_hwm.expression,
        },
    )
    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "already_exists",
            "message": f"HWM with name={hwm.name!r} already exists",
            "details": {
                "entity_type": "HWM",
                "field": "name",
                "value": hwm.name,
            },
        }
    }

    query = select(HWM).where(HWM.id == hwm.id)
    query_result = await async_session.scalars(query)
    hwm_after = query_result.one()

    # Nothing is changed
    assert naturally_equivalent(hwm_after, hwm)


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(None, id="null"),
        pytest.param(123, id="int"),
        pytest.param(123.456, id="float"),
        pytest.param("abc", id="str"),
        pytest.param({"key1": 123}, id="dict[str, int]"),
        pytest.param({"key2": 123.456}, id="dict[str, float]"),
        pytest.param({"key3": "abc"}, id="dict[str, str]"),
        pytest.param([123, 456], id="list[str]"),
        pytest.param([123.456, 234.567], id="list[float]"),
        pytest.param(["item1", "item2"], id="list[str]"),
        pytest.param([{"key1": 123}, {"key2": 234.567}, {"key3": "abc"}], id="list[dict]"),
    ],
)
async def test_create_hwm_value_can_be_any_valid_json(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    new_hwm: HWM,
    async_session: AsyncSession,
    value: Any,
):
    response = await test_client.post(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "namespace_id": namespace.id,
            "name": new_hwm.name,
            "type": new_hwm.type,
            "value": value,
        },
    )
    assert response.status_code == 201

    content = response.json()
    hmw_id = content["id"]
    assert hmw_id
    assert content["name"] == new_hwm.name
    assert content["type"] == new_hwm.type
    assert content["value"] == value

    query = select(HWM).where(HWM.id == hmw_id)
    query_result = await async_session.scalars(query)
    created_hwm = query_result.one()

    # Row is same as in body
    assert created_hwm.name == content["name"]
    assert created_hwm.type == content["type"]
    assert created_hwm.value == content["value"]


@pytest.mark.parametrize(
    "new_hwm",
    [
        pytest.param({"name": ""}, id="empty-name"),
        pytest.param({"name": "a" * 2049}, id="too-long-name"),
        pytest.param({"type": ""}, id="empty-type"),
        pytest.param({"type": "a" * 65}, id="too-long-type"),
    ],
    indirect=True,
)
async def test_create_hwm_invalid_field_length(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    new_hwm: HWM,
    async_session: AsyncSession,
):
    response = await test_client.post(
        "v1/hwm/",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "namespace_id": namespace.id,
            "name": new_hwm.name,
            "type": new_hwm.type,
            "value": None,
        },
    )

    details: list[dict[str, Any]]
    if pydantic_version < "2":
        if len(new_hwm.name) > 2048:
            details = [
                {
                    "location": ["body", "name"],
                    "message": "ensure this value has at most 2048 characters",
                    "code": "value_error.any_str.max_length",
                },
            ]
        elif len(new_hwm.type) > 64:
            details = [
                {
                    "location": ["body", "type"],
                    "message": "ensure this value has at most 64 characters",
                    "code": "value_error.any_str.max_length",
                },
            ]
        else:
            details = [
                {
                    "location": ["body", "type" if not new_hwm.type else "name"],
                    "message": "ensure this value has at least 1 characters",
                    "code": "value_error.any_str.min_length",
                },
            ]
    else:
        if len(new_hwm.name) > 2048:
            details = [
                {
                    "location": ["body", "name"],
                    "message": "String should have at most 2048 characters",
                    "code": "string_too_long",
                    "url": "https://errors.pydantic.dev/2.5/v/string_too_long",
                    "context": {"max_length": 2048},
                    "input": new_hwm.name,
                },
            ]
        elif len(new_hwm.type) > 64:
            details = [
                {
                    "location": ["body", "type"],
                    "message": "String should have at most 64 characters",
                    "code": "string_too_long",
                    "url": "https://errors.pydantic.dev/2.5/v/string_too_long",
                    "context": {"max_length": 64},
                    "input": new_hwm.type,
                },
            ]
        else:
            details = [
                {
                    "location": ["body", "type" if not new_hwm.type else "name"],
                    "message": "String should have at least 1 character",
                    "code": "string_too_short",
                    "url": "https://errors.pydantic.dev/2.5/v/string_too_short",
                    "context": {"min_length": 1},
                    "input": "",
                },
            ]

    expected = {
        "error": {
            "code": "invalid_request",
            "message": "Invalid request",
            "details": details,
        },
    }

    assert response.status_code == 422
    assert response.json() == expected

    # HWM is not created
    query = select(User).where(HWM.name == new_hwm.name)
    result = await async_session.scalars(query)
    created_hwm = result.one_or_none()

    assert not created_hwm

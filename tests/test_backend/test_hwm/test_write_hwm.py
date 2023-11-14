# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import pytest
from sqlalchemy import select

from horizon.backend.db.models import HWM, HWMHistory, Namespace, User
from horizon.backend.settings import Settings

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.asyncio]


async def test_write_hwm_anonymous_user(
    test_client: AsyncClient,
    namespace: Namespace,
    new_hwm: HWM,
):
    response = await test_client.patch(
        f"v1/namespaces/{namespace.name}/hwm/{new_hwm.name}",
        json={
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
        },
    }


async def test_write_hwm_missing_namespace(
    test_client: AsyncClient,
    new_namespace: Namespace,
    access_token: str,
    new_hwm: HWM,
):
    response = await test_client.patch(
        f"v1/namespaces/{new_namespace.name}/hwm/{new_hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
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
            "message": f"Namespace with name='{new_namespace.name}' not found",
            "details": {
                "entity_type": "Namespace",
                "field": "name",
                "value": new_namespace.name,
            },
        },
    }


async def test_write_hwm_create_new(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    user: User,
    new_hwm: HWM,
    async_session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await test_client.patch(
        f"v1/namespaces/{namespace.name}/hwm/{new_hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "description": new_hwm.description,
            "type": new_hwm.type,
            "value": new_hwm.value,
            "entity": new_hwm.entity,
            "expression": new_hwm.expression,
        },
    )
    assert response.status_code == 200

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

    changed_at = datetime.fromisoformat(content["changed_at"])
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


async def test_write_hwm_create_new_minimal(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    user: User,
    new_hwm: HWM,
    async_session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await test_client.patch(
        f"v1/namespaces/{namespace.name}/hwm/{new_hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "type": new_hwm.type,
            "value": None,
        },
    )
    assert response.status_code == 200

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

    changed_at = datetime.fromisoformat(content["changed_at"])
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


@pytest.mark.parametrize(
    "json, missing",
    [
        ({"value": None}, "type"),
        ({"type": "str"}, "value"),
    ],
)
async def test_write_hwm_create_new_not_enough_arguments(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    new_hwm: HWM,
    json: dict,
    missing: str,
):
    response = await test_client.patch(
        f"v1/namespaces/{namespace.name}/hwm/{new_hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json=json,
    )
    assert response.status_code == 417
    assert response.json() == {
        "error": {
            "code": "invalid_value",
            "message": f"HWM has wrong '{missing}' value <unset>",
            "details": {"entity_type": "HWM", "field": missing, "value": "<unset>"},
        },
    }


async def test_write_hwm_create_new_with_same_name_in_different_namespaces(
    test_client: AsyncClient,
    namespaces: list[Namespace],
    access_token: str,
    user: User,
    new_hwm: HWM,
    async_session: AsyncSession,
):
    namespace1, namespace2, *_ = namespaces

    response1 = await test_client.patch(
        f"v1/namespaces/{namespace1.name}/hwm/{new_hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "type": "abc",
            "value": 123,
        },
    )
    assert response1.status_code == 200

    response2 = await test_client.patch(
        f"v1/namespaces/{namespace2.name}/hwm/{new_hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "type": "bcd",
            "value": 234,
        },
    )
    assert response2.status_code == 200

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


async def test_write_hwm_replace_existing(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    user: User,
    hwm: HWM,
    new_hwm: HWM,
    async_session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await test_client.patch(
        f"v1/namespaces/{namespace.name}/hwm/{hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "description": new_hwm.description,
            "type": new_hwm.type,
            "value": new_hwm.value,
            "entity": new_hwm.entity,
            "expression": new_hwm.expression,
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["id"] == hwm.id
    assert content["name"] == hwm.name  # name cannot be changed
    assert content["description"] == new_hwm.description
    assert content["type"] == new_hwm.type
    assert content["value"] == new_hwm.value
    assert content["entity"] == new_hwm.entity
    assert content["expression"] == new_hwm.expression
    assert content["changed_by"] == user.username

    changed_at = datetime.fromisoformat(content["changed_at"])
    assert changed_at >= current_dt >= hwm.changed_at

    query = select(HWM).where(HWM.id == hwm.id)
    query_result = await async_session.scalars(query)
    updated_hwm = query_result.one()

    # Row is same as in body
    assert updated_hwm.name == content["name"]
    assert updated_hwm.description == content["description"]
    assert updated_hwm.type == content["type"]
    assert updated_hwm.value == content["value"]
    assert updated_hwm.entity == content["entity"]
    assert updated_hwm.expression == content["expression"]
    assert updated_hwm.changed_at == changed_at
    assert updated_hwm.changed_by_user_id == user.id
    assert not updated_hwm.is_deleted

    query = select(HWMHistory).where(HWMHistory.hwm_id == hwm.id)
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


@pytest.mark.parametrize(
    "field, is_none",
    [
        ("type", False),
        ("description", False),
        ("value", False),
        ("value", True),
        ("entity", False),
        ("entity", True),
        ("expression", False),
        ("expression", True),
    ],
)
async def test_write_hwm_replace_existing_partial(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    user: User,
    hwm: HWM,
    new_hwm: HWM,
    async_session: AsyncSession,
    field: str,
    is_none: bool,
):
    current_dt = datetime.now(tz=timezone.utc)
    value = None if is_none else getattr(new_hwm, field)

    response = await test_client.patch(
        f"v1/namespaces/{namespace.name}/hwm/{hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            field: value,
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["id"] == hwm.id
    assert content["name"] == hwm.name  # name cannot be changed
    assert content["changed_by"] == user.username
    # if attribute is passed to endpoint, it will be updated
    assert content[field] == value

    for attribute, attr_value in content.items():
        if attribute != field and not attribute.startswith("changed_"):
            # if attribute was not passed, it is left intact
            assert attr_value == getattr(hwm, attribute)

    changed_at = datetime.fromisoformat(content["changed_at"])
    assert changed_at >= current_dt >= hwm.changed_at

    query = select(HWM).where(HWM.id == hwm.id)
    query_result = await async_session.scalars(query)
    updated_hwm = query_result.one()

    # Row is same as in body
    assert updated_hwm.name == content["name"]
    assert updated_hwm.description == content["description"]
    assert updated_hwm.type == content["type"]
    assert updated_hwm.value == content["value"]
    assert updated_hwm.entity == content["entity"]
    assert updated_hwm.expression == content["expression"]
    assert updated_hwm.changed_at == changed_at
    assert updated_hwm.changed_by_user_id == user.id
    assert not updated_hwm.is_deleted

    query = select(HWMHistory).where(HWMHistory.hwm_id == hwm.id)
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


@pytest.mark.parametrize(
    "settings",
    [
        {"server": {"debug": True}},
        {"server": {"debug": False}},
    ],
    indirect=True,
)
async def test_write_hwm_replace_existing_no_data(
    test_client: AsyncClient,
    access_token: str,
    namespace: Namespace,
    hwm: HWM,
    settings: Settings,
):
    response = await test_client.patch(
        f"v1/namespaces/{namespace.name}/hwm/{hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={},
    )
    assert response.status_code == 422
    details: dict[str, Any] = {
        "errors": [
            {
                "code": "value_error",
                "location": ["body", "__root__"],
                "message": "At least one field must be set.",
            }
        ],
    }
    if settings.server.debug:
        details["body"] = {}

    assert response.json() == {
        "error": {
            "code": "invalid_request",
            "message": "Invalid request",
            "details": details,
        }
    }


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
async def test_write_hwm_value_can_be_any_valid_json(
    test_client: AsyncClient,
    namespace: Namespace,
    access_token: str,
    new_hwm: HWM,
    async_session: AsyncSession,
    value: Any,
):
    response = await test_client.patch(
        f"v1/namespaces/{namespace.name}/hwm/{new_hwm.name}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "type": new_hwm.type,
            "value": value,
        },
    )
    assert response.status_code == 200

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

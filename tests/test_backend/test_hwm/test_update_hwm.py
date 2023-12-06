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


async def test_update_hwm_anonymous_user(
    test_client: AsyncClient,
    hwm: HWM,
):
    response = await test_client.patch(
        f"v1/hwm/{hwm.id}",
        json={
            "value": hwm.value,
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


async def test_update_hwm_missing(
    test_client: AsyncClient,
    access_token: str,
    new_hwm: HWM,
):
    response = await test_client.patch(
        f"v1/hwm/{new_hwm.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "value": new_hwm.value,
        },
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


async def test_update_hwm(
    test_client: AsyncClient,
    access_token: str,
    user: User,
    namespace: Namespace,
    hwm: HWM,
    new_hwm: HWM,
    async_session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await test_client.patch(
        f"v1/hwm/{hwm.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": new_hwm.name,
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
    assert content["namespace_id"] == namespace.id  # namespace_id cannot be changed
    assert content["name"] == new_hwm.name
    assert content["description"] == new_hwm.description
    assert content["type"] == new_hwm.type
    assert content["value"] == new_hwm.value
    assert content["entity"] == new_hwm.entity
    assert content["expression"] == new_hwm.expression
    assert content["changed_by"] == user.username

    changed_at = datetime.fromisoformat(content["changed_at"].replace("Z", "+00:00"))
    assert changed_at >= current_dt >= hwm.changed_at

    query = select(HWM).where(HWM.id == hwm.id)
    query_result = await async_session.scalars(query)
    updated_hwm = query_result.one()

    # Row is same as in body
    assert updated_hwm.name == content["name"]
    assert updated_hwm.namespace_id == content["namespace_id"]
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
    updated_hwm_history = query_result.one()

    # Row is same as in body
    assert updated_hwm_history.name == content["name"]
    assert updated_hwm_history.namespace_id == content["namespace_id"]
    assert updated_hwm_history.description == content["description"]
    assert updated_hwm_history.type == content["type"]
    assert updated_hwm_history.value == content["value"]
    assert updated_hwm_history.entity == content["entity"]
    assert updated_hwm_history.expression == content["expression"]
    assert updated_hwm_history.changed_at == changed_at
    assert updated_hwm_history.changed_by_user_id == user.id
    assert not updated_hwm_history.is_deleted


async def test_update_hwm_already_exist(
    test_client: AsyncClient,
    access_token: str,
    hwms: list[HWM],
    async_session: AsyncSession,
):
    hwm1, hwm2, *_ = hwms

    response = await test_client.patch(
        f"v1/hwm/{hwm1.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"name": hwm2.name},
    )
    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "already_exists",
            "message": f"HWM with name={hwm2.name!r} already exists",
            "details": {
                "entity_type": "HWM",
                "field": "name",
                "value": hwm2.name,
            },
        }
    }

    query = select(HWM).where(HWM.id == hwm1.id)
    query_result = await async_session.scalars(query)
    hwm_after = query_result.one()

    # Nothing is changed
    assert naturally_equivalent(hwm_after, hwm1)


@pytest.mark.parametrize(
    "field, is_none",
    [
        ("name", False),
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
async def test_update_hwm_partial(
    test_client: AsyncClient,
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
        f"v1/hwm/{hwm.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            field: value,
        },
    )
    assert response.status_code == 200

    content = response.json()

    # if attribute is passed to endpoint, it will be updated
    assert content[field] == value

    # others are left intact
    may_change = {field, "changed_by", "changed_at"}
    for attribute, attr_value in content.items():
        if attribute not in may_change:
            # if attribute was not passed, it is left intact
            assert attr_value == getattr(hwm, attribute)

    # these ones are always updated
    assert content["changed_by"] == user.username
    changed_at = datetime.fromisoformat(content["changed_at"].replace("Z", "+00:00"))
    assert changed_at >= current_dt >= hwm.changed_at

    query = select(HWM).where(HWM.id == hwm.id)
    query_result = await async_session.scalars(query)
    updated_hwm = query_result.one()

    # Row is same as in body
    assert updated_hwm.name == content["name"]
    assert updated_hwm.namespace_id == content["namespace_id"]
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
    updated_hwm_history = query_result.one()

    # Row is same as in body
    assert updated_hwm_history.name == content["name"]
    assert updated_hwm_history.namespace_id == content["namespace_id"]
    assert updated_hwm_history.description == content["description"]
    assert updated_hwm_history.type == content["type"]
    assert updated_hwm_history.value == content["value"]
    assert updated_hwm_history.entity == content["entity"]
    assert updated_hwm_history.expression == content["expression"]
    assert updated_hwm_history.changed_at == changed_at
    assert updated_hwm_history.changed_by_user_id == user.id
    assert not updated_hwm_history.is_deleted


@pytest.mark.parametrize(
    "settings",
    [
        {"server": {"debug": True}},
        {"server": {"debug": False}},
    ],
    indirect=True,
)
async def test_update_hwm_no_data(
    test_client: AsyncClient,
    access_token: str,
    hwm: HWM,
):
    response = await test_client.patch(
        f"v1/hwm/{hwm.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"unexpected": "value"},
    )
    assert response.status_code == 422

    details: list[dict[str, Any]]
    if pydantic_version < "2":
        details = [
            {
                "location": ["body", "__root__"],
                "code": "value_error",
                "message": "At least one field must be set.",
            }
        ]
    else:
        details = [
            {
                "code": "value_error",
                "location": ["body"],
                "message": "Value error, At least one field must be set.",
                "context": {},
                "input": {"unexpected": "value"},
                "url": "https://errors.pydantic.dev/2.5/v/value_error",
            }
        ]

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
async def test_update_hwm_value_can_be_any_valid_json(
    test_client: AsyncClient,
    access_token: str,
    hwm: HWM,
    async_session: AsyncSession,
    value: Any,
):
    response = await test_client.patch(
        f"v1/hwm/{hwm.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"value": value},
    )
    assert response.status_code == 200

    content = response.json()
    hmw_id = content["id"]
    assert hmw_id
    assert content["value"] == value

    query = select(HWM).where(HWM.id == hmw_id)
    query_result = await async_session.scalars(query)
    updated_hwm = query_result.one()

    # Row is same as in body
    assert updated_hwm.name == content["name"]
    assert updated_hwm.namespace_id == content["namespace_id"]
    assert updated_hwm.description == content["description"]
    assert updated_hwm.type == content["type"]
    assert updated_hwm.value == content["value"]
    assert updated_hwm.entity == content["entity"]
    assert updated_hwm.expression == content["expression"]
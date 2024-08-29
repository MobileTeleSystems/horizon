# SPDX-FileCopyrightText: 2023 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any

import pytest
from pydantic import __version__ as pydantic_version
from sqlalchemy import select
from sqlalchemy_utils.functions import naturally_equivalent

from horizon.backend.db.models import (
    HWM,
    HWMHistory,
    Namespace,
    NamespaceUserRoleInt,
    User,
)

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


@pytest.mark.parametrize(
    "new_hwm",
    [
        pytest.param({"name": "a" * 2048}, id="max-name"),
        pytest.param({"type": "a" * 64}, id="max-type"),
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "user_with_role",
    [
        NamespaceUserRoleInt.SUPERADMIN,
        NamespaceUserRoleInt.OWNER,
        NamespaceUserRoleInt.MAINTAINER,
        NamespaceUserRoleInt.DEVELOPER,
    ],
    indirect=["user_with_role"],
)
async def test_update_hwm(
    test_client: AsyncClient,
    access_token: str,
    user_with_role: None,
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
    assert updated_hwm_history.action == "Updated"


async def test_update_hwm_already_exists(
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
        },
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
    assert updated_hwm_history.action == "Updated"


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
            },
        ]
    else:
        details = [
            {
                "code": "value_error",
                "location": ["body"],
                "message": "Value error, At least one field must be set.",
                "context": {},
                "input": {"unexpected": "value"},
            },
        ]

    assert response.json() == {
        "error": {
            "code": "invalid_request",
            "message": "Invalid request",
            "details": details,
        },
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
async def test_update_hwm_invalid_field_length(
    test_client: AsyncClient,
    access_token: str,
    hwm: HWM,
    new_hwm: HWM,
    async_session: AsyncSession,
):
    response = await test_client.patch(
        f"v1/hwm/{hwm.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={
            "name": new_hwm.name,
            "type": new_hwm.type,
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
                {
                    "location": ["body", "name"],
                    "message": "instance of Unset expected",
                    "code": "type_error.arbitrary_type",
                },
            ]
        elif len(new_hwm.type) > 64:
            details = [
                {
                    "location": ["body", "type"],
                    "message": "ensure this value has at most 64 characters",
                    "code": "value_error.any_str.max_length",
                },
                {
                    "location": ["body", "type"],
                    "message": "instance of Unset expected",
                    "code": "type_error.arbitrary_type",
                },
            ]
        else:
            details = [
                {
                    "location": ["body", "type" if not new_hwm.type else "name"],
                    "message": "ensure this value has at least 1 characters",
                    "code": "value_error.any_str.min_length",
                },
                {
                    "location": ["body", "type" if not new_hwm.type else "name"],
                    "message": "instance of Unset expected",
                    "code": "type_error.arbitrary_type",
                },
            ]
    else:
        if len(new_hwm.name) > 2048:
            details = [
                {
                    "location": ["body", "name"],
                    "message": "Value should have at most 2048 items after validation, not 2049",
                    "code": "too_long",
                    "context": {"max_length": 2048, "actual_length": 2049, "field_type": "Value"},
                    "input": new_hwm.name,
                },
            ]
        elif len(new_hwm.type) > 64:
            details = [
                {
                    "location": ["body", "type"],
                    "message": "Value should have at most 64 items after validation, not 65",
                    "code": "too_long",
                    "context": {"max_length": 64, "actual_length": 65, "field_type": "Value"},
                    "input": new_hwm.type,
                },
            ]
        else:
            details = [
                {
                    "location": ["body", "type" if not new_hwm.type else "name"],
                    "message": "Value should have at least 1 item after validation, not 0",
                    "code": "too_short",
                    "context": {"min_length": 1, "actual_length": 0, "field_type": "Value"},
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

    query = select(HWM).where(HWM.id == hwm.id)
    query_result = await async_session.scalars(query)
    hwm_after = query_result.one()

    # Nothing is changed
    assert naturally_equivalent(hwm_after, hwm)


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
async def test_update_hwm_permission_denied(
    user_with_role: None,
    expected_status: int,
    expected_response: dict,
    test_client: AsyncClient,
    access_token: str,
    hwm: HWM,
):
    response = await test_client.patch(
        f"v1/hwm/{hwm.id}",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"value": "value"},
    )
    assert response.status_code == expected_status
    assert response.json() == expected_response

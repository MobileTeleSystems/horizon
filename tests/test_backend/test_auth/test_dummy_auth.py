# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import secrets
from datetime import datetime, timezone
from time import time
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select
from sqlalchemy_utils.functions import naturally_equivalent

from horizon.backend.db.models import User
from horizon.backend.settings.auth.jwt import JWTSettings
from horizon.backend.utils.jwt import decode_jwt

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

    from horizon.backend.settings import Settings

pytestmark = [pytest.mark.asyncio, pytest.mark.dummy_auth, pytest.mark.auth]


@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"class": "horizon.backend.providers.auth.dummy.DummyAuthProvider"}},
    ],
    indirect=True,
)
async def test_dummy_auth_get_token_creates_user(
    test_client: AsyncClient,
    new_user: User,
    access_token_settings: JWTSettings,
    async_session: AsyncSession,
):
    current_dt = datetime.now(tz=timezone.utc)

    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": new_user.username,
            "password": secrets.token_hex(16),
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["access_token"]
    assert content["token_type"] == "bearer"
    assert time() < content["expires_at"] <= time() + access_token_settings.expire_seconds

    jwt = decode_jwt(
        content["access_token"],
        access_token_settings.secret_key,
        access_token_settings.security_algorithm,
    )
    user_id = jwt["user_id"]
    assert user_id

    query = select(User).where(User.id == user_id)
    users = await async_session.scalars(query)
    created_user = users.one()

    assert created_user.username == new_user.username
    assert created_user.created_at >= current_dt
    assert created_user.updated_at >= current_dt
    assert created_user.is_active
    assert not created_user.is_deleted


@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"class": "horizon.backend.providers.auth.dummy.DummyAuthProvider"}},
    ],
    indirect=True,
)
async def test_dummy_auth_get_token_for_existing_user(
    test_client: AsyncClient,
    user: User,
    access_token_settings: JWTSettings,
    async_session: AsyncSession,
):
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": secrets.token_hex(16),
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["access_token"]
    assert content["token_type"] == "bearer"
    assert time() < content["expires_at"] <= time() + access_token_settings.expire_seconds

    jwt = decode_jwt(
        content["access_token"],
        access_token_settings.secret_key,
        access_token_settings.security_algorithm,
    )
    user_id = jwt["user_id"]
    assert user_id == user.id

    query = select(User).where(User.id == user.id)
    query_result = await async_session.scalars(query)
    user_after = query_result.one()

    # Nothing is changed
    assert naturally_equivalent(user_after, user)


@pytest.mark.parametrize("user", [{"is_active": False}], indirect=True)
@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"class": "horizon.backend.providers.auth.dummy.DummyAuthProvider"}},
    ],
    indirect=True,
)
async def test_dummy_auth_get_token_for_inactive_user(
    test_client: AsyncClient,
    user: User,
):
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": secrets.token_hex(16),
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": f"User '{user.username}' is disabled",
        },
    }


@pytest.mark.parametrize("user", [{"is_deleted": True}], indirect=True)
@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"class": "horizon.backend.providers.auth.dummy.DummyAuthProvider"}},
    ],
    indirect=True,
)
async def test_dummy_auth_get_token_for_deleted_user(
    test_client: AsyncClient,
    user: User,
):
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": secrets.token_hex(16),
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"User with username='{user.username}' not found",
            "details": {
                "entity_type": "User",
                "field": "username",
                "value": user.username,
            },
        },
    }


@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"class": "horizon.backend.providers.auth.dummy.DummyAuthProvider"}, "server": {"debug": True}},
        {"auth": {"class": "horizon.backend.providers.auth.dummy.DummyAuthProvider"}, "server": {"debug": False}},
    ],
    indirect=True,
)
async def test_dummy_auth_get_token_with_malformed_input(
    test_client: AsyncClient,
    new_user: User,
    settings: Settings,
):
    username = new_user.username
    password = secrets.token_hex(16)

    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": username,
            "passwor": password,
        },
    )

    expected = {
        "error": {
            "code": "invalid_request",
            "message": "Invalid request",
            "details": {
                "errors": [
                    {
                        "location": ["body", "password"],
                        "code": "value_error.missing",
                        "message": "field required",
                    },
                ],
            },
        },
    }

    if settings.server.debug:
        # don't print error details in production
        expected["error"]["details"]["body"] = {"username": username, "passwor": password}

    assert response.status_code == 422
    assert response.json() == expected


@pytest.mark.parametrize("user", [{"is_active": False}], indirect=True)
@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"class": "horizon.backend.providers.auth.dummy.DummyAuthProvider"}},
    ],
    indirect=True,
)
async def test_dummy_auth_check_inactive_user(
    test_client: AsyncClient,
    access_token: str,
    user: User,
):
    response = await test_client.get(
        "v1/namespaces/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": f"User '{user.username}' is disabled",
        },
    }


@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"class": "horizon.backend.providers.auth.dummy.DummyAuthProvider"}},
    ],
    indirect=True,
)
async def test_dummy_auth_check_missing_user(
    test_client: AsyncClient,
    fake_access_token: str,
    new_user: User,
):
    response = await test_client.get(
        "v1/namespaces/",
        headers={"Authorization": f"Bearer {fake_access_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"User with id={new_user.id} not found",
            "details": {
                "entity_type": "User",
                "field": "id",
                "value": new_user.id,
            },
        },
    }


@pytest.mark.parametrize("user", [{"is_deleted": True}], indirect=True)
@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"class": "horizon.backend.providers.auth.dummy.DummyAuthProvider"}},
    ],
    indirect=True,
)
async def test_dummy_auth_check_disabled_user(
    test_client: AsyncClient,
    access_token: str,
    user: User,
):
    response = await test_client.get(
        "v1/namespaces/",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"User with id={user.id} not found",
            "details": {
                "entity_type": "User",
                "field": "id",
                "value": user.id,
            },
        },
    }


@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"class": "horizon.backend.providers.auth.dummy.DummyAuthProvider"}},
    ],
    indirect=True,
)
async def test_dummy_auth_check_invalid_token(
    test_client: AsyncClient,
    invalid_access_token: str,
):
    response = await test_client.get(
        "v1/namespaces/",
        headers={"Authorization": f"Bearer {invalid_access_token}"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Invalid token",
        },
    }

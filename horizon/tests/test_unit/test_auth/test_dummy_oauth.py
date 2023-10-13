from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

import pytest
from sqlalchemy import select

from app.db.models.user import User
from app.utils.jwt import decode_jwt

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.settings import Settings

pytestmark = [pytest.mark.asyncio]


async def test_dummy_auth_get_token_creates_user(
    client: AsyncClient,
    new_user: User,
    settings: Settings,
    session: AsyncSession,
):
    response = await client.post(
        "v1/auth/token",
        data={
            "username": new_user.username,
            "password": secrets.token_hex(16),
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["access_token"]
    assert content["refresh_token"] == "refresh_token"
    assert content["token_type"] == "bearer"

    jwt = decode_jwt(content["access_token"], settings.jwt)
    user_id = jwt["user_id"]
    assert user_id

    query = select(User).where(User.id == user_id)
    users = await session.scalars(query)
    created_user = users.one()

    assert created_user.username == new_user.username
    assert created_user.is_active
    assert not created_user.is_deleted


async def test_dummy_auth_get_token_for_existing_user(
    client: AsyncClient,
    user: User,
    settings: Settings,
):
    response = await client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": secrets.token_hex(16),
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["access_token"]
    assert content["refresh_token"] == "refresh_token"
    assert content["token_type"] == "bearer"

    jwt = decode_jwt(content["access_token"], settings.jwt)
    user_id = jwt["user_id"]
    assert user_id == user.id


@pytest.mark.parametrize("user", [{"is_active": False}], indirect=True)
async def test_dummy_auth_get_token_for_inactive_user(
    client: AsyncClient,
    user: User,
):
    response = await client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": secrets.token_hex(16),
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "not_authorized",
            "message": f"User '{user.username}' is disabled",
        },
    }


@pytest.mark.parametrize("user", [{"is_deleted": True}], indirect=True)
async def test_dummy_auth_get_token_for_deleted_user(
    client: AsyncClient,
    user: User,
):
    response = await client.post(
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
        {"jwt": {"secret_key": None}, "server": {"debug": True}},
        {"jwt": {"secret_key": None}, "server": {"debug": False}},
    ],
    indirect=True,
)
async def test_dummy_auth_get_token_with_missing_jwt_secret(
    client: AsyncClient,
    new_user: User,
    settings: Settings,
):
    response = await client.post(
        "v1/auth/token",
        data={
            "username": new_user.username,
            "password": secrets.token_hex(16),
        },
    )
    expected = {
        "error": {
            "code": "unknown",
            "message": "Got unhandled exception. Please contact support",
        },
    }

    if settings.server.debug:
        # don't print error details in production
        expected["error"]["details"] = ["Expected settings.jwt.secret_key to be set, got None"]

    assert response.status_code == 500
    assert response.json() == expected


@pytest.mark.parametrize(
    "settings",
    [
        {"server": {"debug": True}},
        {"server": {"debug": False}},
    ],
    indirect=True,
)
async def test_dummy_auth_get_token_with_malformed_input(
    client: AsyncClient,
    new_user: User,
    settings: Settings,
):
    username = new_user.username
    password = secrets.token_hex(16)

    response = await client.post(
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

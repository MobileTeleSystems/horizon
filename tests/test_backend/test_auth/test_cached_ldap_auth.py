# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import secrets
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from time import time
from typing import TYPE_CHECKING, Any

import pytest
from fastapi import FastAPI
from passlib.hash import argon2
from pydantic import __version__ as pydantic_version
from sqlalchemy import select
from sqlalchemy_utils.functions import naturally_equivalent

from horizon.backend.db.models import CredentialsCache, User
from horizon.backend.providers.auth.cached_ldap import CachedLDAPAuthProvider
from horizon.backend.settings import Settings
from horizon.backend.settings.auth.jwt import JWTSettings
from horizon.backend.utils.jwt import decode_jwt

if TYPE_CHECKING:
    from httpx import AsyncClient
    from sqlalchemy.ext.asyncio import AsyncSession

CACHED_LDAP = "horizon.backend.providers.auth.cached_ldap.CachedLDAPAuthProvider"
pytestmark = [pytest.mark.asyncio, pytest.mark.ldap_auth, pytest.mark.auth, pytest.mark.backend]


@pytest.mark.parametrize("new_user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize("settings", [{"auth": {"provider": CACHED_LDAP}}], indirect=True)
async def test_cached_ldap_auth_get_token_creates_user(
    test_client: AsyncClient,
    async_session: AsyncSession,
    new_user: User,
    access_token_settings: JWTSettings,
):
    current_dt = datetime.now(tz=timezone.utc)
    before = time()

    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": new_user.username,
            "password": "password",
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["access_token"]
    assert content["token_type"] == "bearer"
    assert before < content["expires_at"] <= time() + access_token_settings.expire_seconds

    jwt = decode_jwt(
        content["access_token"],
        access_token_settings.secret_key.get_secret_value(),
        access_token_settings.security_algorithm,
    )
    user_id = jwt["user_id"]
    assert user_id

    # User is created
    query = select(User).where(User.id == user_id)
    users = await async_session.scalars(query)
    created_user = users.one()

    assert created_user.username == new_user.username
    assert created_user.created_at >= current_dt
    assert created_user.updated_at >= current_dt
    assert created_user.is_active

    # credentials cache is updated
    query = select(CredentialsCache).where(CredentialsCache.user_id == user_id)
    cache = await async_session.scalars(query)
    cache_item = cache.one()

    assert cache_item.login == new_user.username
    assert cache_item.created_at >= current_dt
    assert cache_item.updated_at >= current_dt
    assert argon2.verify("password", cache_item.password_hash)


@pytest.mark.parametrize("user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize("settings", [{"auth": {"provider": CACHED_LDAP}}], indirect=True)
async def test_cached_ldap_auth_get_token_for_existing_user(
    test_client: AsyncClient,
    async_session: AsyncSession,
    user: User,
    access_token_settings: JWTSettings,
):
    current_dt = datetime.now(tz=timezone.utc)
    before = time()
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": "password",
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["access_token"]
    assert content["token_type"] == "bearer"
    assert before < content["expires_at"] <= time() + access_token_settings.expire_seconds

    jwt = decode_jwt(
        content["access_token"],
        access_token_settings.secret_key.get_secret_value(),
        access_token_settings.security_algorithm,
    )
    user_id = jwt["user_id"]
    assert user_id == user.id

    query = select(User).where(User.id == user.id)
    query_result = await async_session.scalars(query)
    user_after = query_result.one()

    # user is not changed
    assert naturally_equivalent(user_after, user)

    # credentials cache is updated
    query = select(CredentialsCache).where(CredentialsCache.user_id == user.id)
    cache = await async_session.scalars(query)
    cache_item = cache.one()

    assert cache_item.login == user.username
    assert cache_item.created_at >= current_dt
    assert cache_item.updated_at >= current_dt
    assert argon2.verify("password", cache_item.password_hash)


@pytest.mark.parametrize("new_user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize("settings", [{"auth": {"provider": CACHED_LDAP}}], indirect=True)
async def test_cached_ldap_auth_get_token_with_wrong_password(
    test_client: AsyncClient,
    async_session: AsyncSession,
    new_user: User,
):
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": new_user.username,
            "password": secrets.token_hex(16),
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Wrong credentials",
            "details": None,
        },
    }

    # user is not created
    query = select(User).where(User.username == new_user.username)
    users = await async_session.scalars(query)
    created_user = users.one_or_none()

    assert not created_user

    # credentials are not cached
    query = select(CredentialsCache).where(CredentialsCache.login == new_user.username)
    cache = await async_session.scalars(query)
    cache_item = cache.one_or_none()

    assert not cache_item


@pytest.mark.parametrize("new_user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"provider": CACHED_LDAP, "ldap": {"lookup": {"query_template": "(mail={login})"}}}},
    ],
    indirect=True,
)
async def test_cached_ldap_auth_get_token_with_lookup_by_custom_attribute(
    test_client: AsyncClient,
    async_session: AsyncSession,
    new_user: User,
    access_token_settings: JWTSettings,
):
    current_dt = datetime.now(tz=timezone.utc)
    before = time()

    response = await test_client.post(
        "v1/auth/token",
        data={
            # lookup user in LDAPAuthProvider by email
            "username": "developer.one@ldapmock.local",
            "password": "password",
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["access_token"]
    assert content["token_type"] == "bearer"
    assert before < content["expires_at"] <= time() + access_token_settings.expire_seconds

    jwt = decode_jwt(
        content["access_token"],
        access_token_settings.secret_key.get_secret_value(),
        access_token_settings.security_algorithm,
    )
    user_id = jwt["user_id"]
    assert user_id

    query = select(User).where(User.id == user_id)
    users = await async_session.scalars(query)
    created_user = users.one()

    # but user in internal table was created with username = `uid_attribute`
    assert created_user.username == new_user.username
    assert created_user.created_at >= current_dt
    assert created_user.updated_at >= current_dt
    assert created_user.is_active

    # credentials cache is updated, containing login == user email
    query = select(CredentialsCache).where(CredentialsCache.user_id == user_id)
    cache = await async_session.scalars(query)
    cache_item = cache.one()

    assert cache_item.login == "developer.one@ldapmock.local"
    assert cache_item.created_at >= current_dt
    assert cache_item.updated_at >= current_dt
    assert argon2.verify("password", cache_item.password_hash)


@pytest.mark.parametrize("new_user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"provider": CACHED_LDAP, "ldap": {"lookup": {"query_template": "(mail={login})"}}}},
        {"auth": {"provider": CACHED_LDAP, "ldap": {"uid_attribute": "mail"}}},
        {"auth": {"provider": CACHED_LDAP, "ldap": {"base_dn": "dc=unknown,dc=company"}}},
    ],
    indirect=True,
)
async def test_cached_ldap_auth_get_token_with_wrong_lookup_settings(
    test_client: AsyncClient,
    async_session: AsyncSession,
    new_user: User,
):
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": new_user.username,
            "password": "password",
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"User with username={new_user.username!r} not found",
            "details": {
                "entity_type": "User",
                "field": "username",
                "value": new_user.username,
            },
        },
    }

    # user is not created
    query = select(User).where(User.username == new_user.username)
    users = await async_session.scalars(query)
    created_user = users.one_or_none()

    assert not created_user

    # credentials are not cached
    query = select(CredentialsCache).where(CredentialsCache.login == new_user.username)
    cache = await async_session.scalars(query)
    cache_item = cache.one_or_none()

    assert not cache_item


@pytest.mark.parametrize("user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize(
    "settings",
    [{"auth": {"provider": CACHED_LDAP, "ldap": {"lookup": {"enabled": False}}}}],
    indirect=True,
)
async def test_cached_ldap_auth_get_token_without_lookup(
    test_client: AsyncClient,
    async_session: AsyncSession,
    user: User,
    access_token_settings: JWTSettings,
):
    current_dt = datetime.now(tz=timezone.utc)
    before = time()
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": "password",
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["access_token"]
    assert content["token_type"] == "bearer"
    assert before < content["expires_at"] <= time() + access_token_settings.expire_seconds

    jwt = decode_jwt(
        content["access_token"],
        access_token_settings.secret_key.get_secret_value(),
        access_token_settings.security_algorithm,
    )
    user_id = jwt["user_id"]
    assert user_id == user.id

    query = select(User).where(User.id == user.id)
    query_result = await async_session.scalars(query)
    user_after = query_result.one()

    # user is not changed
    assert naturally_equivalent(user_after, user)

    # credentials cache is updated
    query = select(CredentialsCache).where(CredentialsCache.user_id == user.id)
    cache = await async_session.scalars(query)
    cache_item = cache.one()

    assert cache_item.login == user.username
    assert cache_item.created_at >= current_dt
    assert cache_item.updated_at >= current_dt
    assert argon2.verify("password", cache_item.password_hash)


@pytest.mark.parametrize("new_user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize(
    "settings",
    [
        {"auth": {"provider": CACHED_LDAP, "ldap": {"lookup": {"enabled": False}, "uid_attribute": "mail"}}},
        {"auth": {"provider": CACHED_LDAP, "ldap": {"lookup": {"enabled": False}, "base_dn": "dc=unknown,dc=company"}}},
        {"auth": {"provider": CACHED_LDAP, "ldap": {"lookup": {"enabled": False}, "bind_dn_template": "{login}"}}},
    ],
    indirect=True,
)
async def test_cached_ldap_auth_get_token_without_lookup_wrong_settings(
    test_client: AsyncClient,
    async_session: AsyncSession,
    new_user: User,
):
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": new_user.username,
            "password": "password",
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Wrong credentials",
            "details": None,
        },
    }

    # user is not created
    query = select(User).where(User.username == new_user.username)
    users = await async_session.scalars(query)
    created_user = users.one_or_none()

    assert not created_user

    # credentials are not cached
    query = select(CredentialsCache).where(CredentialsCache.login == new_user.username)
    cache = await async_session.scalars(query)
    cache_item = cache.one_or_none()

    assert not cache_item


@pytest.mark.parametrize("settings", [{"auth": {"provider": CACHED_LDAP}}], indirect=True)
@pytest.mark.parametrize("new_user", [{"username": "missing"}], indirect=True)
async def test_cached_ldap_auth_get_token_for_missing_user_from_both_ldap_and_internal_database(
    test_client: AsyncClient,
    async_session: AsyncSession,
    new_user: User,
):
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": new_user.username,
            "password": secrets.token_hex(16),
        },
    )
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "not_found",
            "message": f"User with username={new_user.username!r} not found",
            "details": {
                "entity_type": "User",
                "field": "username",
                "value": new_user.username,
            },
        },
    }

    query = select(User).where(User.username == new_user.username)
    users = await async_session.scalars(query)
    created_user = users.one_or_none()

    assert not created_user

    # credentials are not cached
    query = select(CredentialsCache).where(CredentialsCache.login == new_user.username)
    cache = await async_session.scalars(query)
    cache_item = cache.one_or_none()

    assert not cache_item


@pytest.mark.parametrize("settings", [{"auth": {"provider": CACHED_LDAP}}], indirect=True)
@pytest.mark.parametrize("user", [{"username": "missing"}], indirect=True)
async def test_cached_ldap_auth_get_token_for_missing_user_from_ldap(
    test_client: AsyncClient,
    async_session: AsyncSession,
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
            "message": f"User with username={user.username!r} not found",
            "details": {
                "entity_type": "User",
                "field": "username",
                "value": user.username,
            },
        },
    }

    # credentials are not cached
    query = select(CredentialsCache).where(CredentialsCache.user_id == user.id)
    cache = await async_session.scalars(query)
    cache_item = cache.one_or_none()

    assert not cache_item


@pytest.mark.parametrize("user", [{"username": "developer1", "is_active": False}], indirect=True)
@pytest.mark.parametrize("settings", [{"auth": {"provider": CACHED_LDAP}}], indirect=True)
async def test_cached_ldap_auth_get_token_for_inactive_user(
    test_client: AsyncClient,
    async_session: AsyncSession,
    user: User,
):
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": "password",
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": f"User {user.username!r} is disabled",
            "details": None,
        },
    }

    # credentials are not cached
    query = select(CredentialsCache).where(CredentialsCache.user_id == user.id)
    cache = await async_session.scalars(query)
    cache_item = cache.one_or_none()

    assert not cache_item


@pytest.mark.parametrize("settings", [{"auth": {"provider": CACHED_LDAP}}], indirect=True)
async def test_cached_ldap_auth_get_token_with_malformed_input(
    test_client: AsyncClient,
    async_session: AsyncSession,
    new_user: User,
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

    details: list[dict[str, Any]]
    if pydantic_version < "2":
        details = [
            {
                "location": ["body", "password"],
                "message": "field required",
                "code": "value_error.missing",
            },
        ]
    else:
        details = [
            {
                "location": ["body", "password"],
                "message": "Field required",
                "code": "missing",
                "context": {},
                "input": None,
                "url": "https://errors.pydantic.dev/2.5/v/missing",
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

    # user is not created
    query = select(User).where(User.username == username)
    users = await async_session.scalars(query)
    created_user = users.one_or_none()

    assert not created_user

    # credentials are not cached
    query = select(CredentialsCache).where(CredentialsCache.login == username)
    cache = await async_session.scalars(query)
    cache_item = cache.one_or_none()

    assert not cache_item


@pytest.mark.parametrize("user", [{"username": "developer1", "is_active": False}], indirect=True)
@pytest.mark.parametrize("settings", [{"auth": {"provider": CACHED_LDAP}}], indirect=True)
async def test_cached_ldap_auth_check_inactive_user(
    test_client: AsyncClient,
    async_session: AsyncSession,
    access_token: str,
    user: User,
):
    response = await test_client.get(
        "v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": f"User {user.username!r} is disabled",
            "details": None,
        },
    }


@pytest.mark.parametrize("user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize(
    "settings",
    [
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": True}},
                },
            },
        },
        {
            "server": {"debug": True},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": True}},
                },
            },
        },
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": False}},
                },
            },
        },
        {
            "server": {"debug": True},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": False}},
                },
            },
        },
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": False},
                },
            },
        },
        {
            "server": {"debug": True},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": False},
                },
            },
        },
    ],
    indirect=True,
)
async def test_cached_ldap_auth_get_token_ldap_is_unavailable_but_credentials_cache_item_is_missing(
    test_client: AsyncClient,
    async_session: AsyncSession,
    settings: Settings,
    user: User,
):
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": "password",
        },
    )
    assert response.status_code == 503

    details: str | None = None
    if settings.server.debug:
        details = "Failed to connect to LDAP"

    assert response.json() == {
        "error": {
            "code": "service_unavailable",
            "message": "Service unavailable",
            "details": details,
        },
    }

    # credentials are not cached
    query = select(CredentialsCache).where(CredentialsCache.user_id == user.id)
    cache = await async_session.scalars(query)
    cache_item = cache.one_or_none()

    assert not cache_item


@pytest.mark.parametrize("user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize(
    "credentials_cache_item",
    [{"login": "developer1", "password_hash": argon2.hash("password")}],
    indirect=True,
)
@pytest.mark.parametrize(
    "settings",
    [
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": True}},
                },
            },
        },
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": False}},
                },
            },
        },
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": False},
                },
            },
        },
    ],
    indirect=True,
)
async def test_cached_ldap_auth_get_token_ldap_is_unavailable_but_credentials_cache_is_up_to_date(
    test_client: AsyncClient,
    async_session: AsyncSession,
    settings: Settings,
    user: User,
    credentials_cache_item: CredentialsCache,
    access_token_settings: JWTSettings,
):
    before = time()
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": "password",
        },
    )
    assert response.status_code == 200

    content = response.json()
    assert content["access_token"]
    assert content["token_type"] == "bearer"
    assert before < content["expires_at"] <= time() + access_token_settings.expire_seconds

    # credentials cache item is not updated
    query = select(CredentialsCache).where(CredentialsCache.user_id == user.id)
    cache = await async_session.scalars(query)
    cache_item = cache.one_or_none()

    assert naturally_equivalent(cache_item, credentials_cache_item)


@pytest.mark.parametrize("user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize(
    "credentials_cache_item",
    [
        {
            "login": "developer1",
            "password_hash": argon2.hash("password"),
            "updated_at": datetime.now(tz=timezone.utc) - timedelta(days=1),
        },
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "settings",
    [
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": True}},
                },
            },
        },
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": False}},
                },
            },
        },
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": False},
                },
            },
        },
    ],
    indirect=True,
)
async def test_cached_ldap_auth_get_token_ldap_is_unavailable_and_credentials_cache_is_expired(
    test_client: AsyncClient,
    async_session: AsyncSession,
    settings: Settings,
    user: User,
    credentials_cache_item: CredentialsCache,
):
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": "password",
        },
    )
    assert response.status_code == 503
    assert response.json() == {
        "error": {
            "code": "service_unavailable",
            "message": "Service unavailable",
            "details": None,
        },
    }
    # credentials cache item is not updated
    query = select(CredentialsCache).where(CredentialsCache.user_id == user.id)
    cache = await async_session.scalars(query)
    cache_item = cache.one_or_none()

    assert naturally_equivalent(cache_item, credentials_cache_item)


@pytest.mark.parametrize("user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize(
    "credentials_cache_item",
    [
        {
            "login": "developer1",
            "password_hash": argon2.hash("wrong_password"),
        },
    ],
    indirect=True,
)
@pytest.mark.parametrize(
    "settings",
    [
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": True}},
                },
            },
        },
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": False}},
                },
            },
        },
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "url": "ldap://unknown.host",
                    "lookup": {"enabled": False},
                },
            },
        },
    ],
    indirect=True,
)
async def test_cached_ldap_auth_get_token_ldap_is_unavailable_and_credentials_cache_contains_wrong_password_hash(
    test_client: AsyncClient,
    async_session: AsyncSession,
    user: User,
    credentials_cache_item: CredentialsCache,
):
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": "password",
        },
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Wrong credentials",
            "details": None,
        },
    }
    # credentials cache item is not updated
    query = select(CredentialsCache).where(CredentialsCache.user_id == user.id)
    cache = await async_session.scalars(query)
    cache_item = cache.one_or_none()

    assert naturally_equivalent(cache_item, credentials_cache_item)


@pytest.mark.parametrize("user", [{"username": "developer1"}], indirect=True)
@pytest.mark.parametrize(
    "settings",
    [
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": True}},
                },
            },
        },
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "lookup": {"enabled": True, "check_on_startup": False, "pool": {"enabled": False}},
                },
            },
        },
        {
            "server": {"debug": False},
            "auth": {
                "provider": CACHED_LDAP,
                "ldap": {
                    "lookup": {"enabled": False},
                },
            },
        },
    ],
    indirect=True,
)
async def test_cached_ldap_auth_get_token_ldap_is_unavailable_but_then_restored(
    test_client: AsyncClient,
    settings: Settings,
    test_app: FastAPI,
    user: User,
):
    # patch application to make all LDAP connections failing
    valid_settings = deepcopy(settings.auth)
    settings.auth.ldap["url"] = "ldap://unknown.host"

    CachedLDAPAuthProvider.setup(test_app)
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": "password",
        },
    )
    assert response.status_code == 503

    settings.auth = valid_settings
    CachedLDAPAuthProvider.setup(test_app)
    response = await test_client.post(
        "v1/auth/token",
        data={
            "username": user.username,
            "password": "password",
        },
    )
    assert response.status_code == 200


# LDAP is not accessed while checking access token to avoid calling it on each incoming request
# so check is successful even for username missing in LDAP
@pytest.mark.parametrize("user", [{"username": "developer1"}, {"username": "unknown"}], indirect=True)
@pytest.mark.parametrize("settings", [{"auth": {"provider": CACHED_LDAP}}], indirect=True)
async def test_cached_ldap_auth_check(
    test_client: AsyncClient,
    access_token: str,
):
    response = await test_client.get(
        "v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200


@pytest.mark.parametrize("new_user", [{"username": "developer1"}, {"username": "unknown"}], indirect=True)
@pytest.mark.parametrize("settings", [{"auth": {"provider": CACHED_LDAP}}], indirect=True)
async def test_cached_ldap_auth_check_missing_user(
    test_client: AsyncClient,
    fake_access_token: str,
    new_user: User,
):
    response = await test_client.get(
        "v1/users/me",
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


@pytest.mark.parametrize("settings", [{"auth": {"provider": CACHED_LDAP}}], indirect=True)
async def test_cached_ldap_auth_check_invalid_token(
    test_client: AsyncClient,
    invalid_access_token: str,
):
    response = await test_client.get(
        "v1/users/me",
        headers={"Authorization": f"Bearer {invalid_access_token}"},
    )
    assert response.status_code == 401
    assert response.json() == {
        "error": {
            "code": "unauthorized",
            "message": "Invalid token",
            "details": None,
        },
    }

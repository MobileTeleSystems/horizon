# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from time import time
from typing import TYPE_CHECKING

import pytest
from pytest_lazyfixture import lazy_fixture

from horizon.backend.settings.auth.jwt import JWTSettings
from horizon.backend.utils.jwt import sign_jwt

if TYPE_CHECKING:
    from horizon.backend.db.models import User
    from horizon.backend.settings import Settings

pytestmark = [pytest.mark.auth]


@pytest.fixture
def access_token_settings(settings: Settings) -> JWTSettings:
    return JWTSettings.parse_obj(settings.auth.access_token)


@pytest.fixture
def fake_access_token(new_user: User, access_token_settings: JWTSettings):
    return sign_jwt(
        {"user_id": new_user.id, "exp": time() + 1000},
        access_token_settings.secret_key,
        access_token_settings.security_algorithm,
    )


@pytest.fixture
def access_token_wrong_secret_key(user: User, access_token_settings: JWTSettings):
    return sign_jwt({"user_id": user.id, "exp": time() + 1000}, "wrong", access_token_settings.security_algorithm)


@pytest.fixture
def access_token_wrong_algorithm(user: User, access_token_settings: JWTSettings):
    return sign_jwt({"user_id": user.id, "exp": time() + 1000}, access_token_settings.secret_key, "HS512")


@pytest.fixture
def access_token_without_user_id(user: User, access_token_settings: JWTSettings):
    return sign_jwt(
        {"userid": user.id, "exp": time() + 1000},
        access_token_settings.secret_key,
        access_token_settings.security_algorithm,
    )


@pytest.fixture
def access_token_with_wrong_user_id_type(user: User, access_token_settings: JWTSettings):
    return sign_jwt(
        {"user_id": "abc", "exp": time() + 1000},
        access_token_settings.secret_key,
        access_token_settings.security_algorithm,
    )


@pytest.fixture
def access_token_expired(user: User, access_token_settings: JWTSettings):
    return sign_jwt(
        {"user_id": user.id, "exp": time() - 1000},
        access_token_settings.secret_key,
        access_token_settings.security_algorithm,
    )


@pytest.fixture(
    params=[
        lazy_fixture("access_token_wrong_secret_key"),
        lazy_fixture("access_token_wrong_algorithm"),
        lazy_fixture("access_token_without_user_id"),
        lazy_fixture("access_token_with_wrong_user_id_type"),
        lazy_fixture("access_token_expired"),
    ],
)
def invalid_access_token(request: pytest.FixtureRequest):
    return request.param


@pytest.fixture
def access_token(user: User, access_token_settings: JWTSettings):
    return sign_jwt(
        {"user_id": user.id, "exp": time() + 1000},
        access_token_settings.secret_key,
        access_token_settings.security_algorithm,
    )

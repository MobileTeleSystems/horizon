# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from freezegun import freeze_time
from pytest_lazyfixture import lazy_fixture

from horizon.backend.utils.jwt import sign_jwt

if TYPE_CHECKING:
    from horizon.backend.db.models import User
    from horizon.backend.settings import Settings

pytestmark = [pytest.mark.auth]


@pytest.fixture
def fake_access_token(new_user: User, settings: Settings):
    return sign_jwt({"user_id": new_user.id}, settings.jwt)


@pytest.fixture
def access_token_wrong_secret_key(user: User, settings: Settings):
    jwt = settings.jwt.copy(update={"secret_key": "wrong"})
    return sign_jwt({"user_id": user.id}, jwt)


@pytest.fixture
def access_token_wrong_algorithm(user: User, settings: Settings):
    jwt = settings.jwt.copy(update={"security_algorithm": "HS512"})
    return sign_jwt({"user_id": user.id}, jwt)


@pytest.fixture
def access_token_without_user_id(user: User, settings: Settings):
    return sign_jwt({"userid": user.id}, settings.jwt)


@pytest.fixture
def access_token_with_wrong_user_id_type(user: User, settings: Settings):
    return sign_jwt({"user_id": "abc"}, settings.jwt)


@pytest.fixture
def access_token_expired(user: User, settings: Settings):
    with freeze_time("2021-01-01"):
        result = sign_jwt({"user_id": user.id}, settings.jwt)
    return result


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
def access_token(user: User, settings: Settings):
    return sign_jwt({"user_id": user.id}, settings.jwt)

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import pytest
from authlib.oauth2.auth import OAuth2Token as AuthlibToken
from pytest_lazyfixture import lazy_fixture

from horizon.backend.db.models import User
from horizon.client.auth import AccessToken, LoginPassword
from horizon.client.sync import HorizonClientSync
from horizon.commons.exceptions.auth import AuthorizationError

pytestmark = [pytest.mark.client_sync, pytest.mark.client, pytest.mark.auth]


def test_sync_client_authorize_with_login_password(external_app_url: str, user: User):
    sync_client = HorizonClientSync(
        base_url=external_app_url,
        auth=LoginPassword(login=user.username, password="test"),
    )
    sync_client.authorize()
    assert sync_client.session.token
    assert isinstance(sync_client.session.token, AuthlibToken)


def test_sync_client_authorize_with_access_token(external_app_url: str, access_token: AccessToken):
    sync_client = HorizonClientSync(base_url=external_app_url, auth=AccessToken(token=access_token))
    sync_client.authorize()
    assert sync_client.session.token
    assert isinstance(sync_client.session.token, AuthlibToken)


@pytest.mark.parametrize(
    "wrong_access_token",
    [
        lazy_fixture("access_token_wrong_secret_key"),
        lazy_fixture("access_token_wrong_algorithm"),
        lazy_fixture("access_token_without_user_id"),
        lazy_fixture("access_token_with_wrong_user_id_type"),
        # expired and malformed tokens are tested in test_access_token_constructor
    ],
)
def test_sync_client_authorize_with_wrong_access_token(external_app_url: str, wrong_access_token: AccessToken):
    sync_client = HorizonClientSync(base_url=external_app_url, auth=AccessToken(token=wrong_access_token))
    with pytest.raises(AuthorizationError):
        sync_client.authorize()

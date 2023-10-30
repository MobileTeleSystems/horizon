# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import pytest
from authlib.integrations.base_client.errors import UnsupportedTokenTypeError
from authlib.oauth2.auth import OAuth2Token as AuthlibToken

from horizon_client.auth import AccessToken, OAuth2Password
from horizon_client.client.sync import HorizonClientSync


def test_sync_client_auth_oauth2_password(external_app_url: str, app_oauth2_password: OAuth2Password):
    sync_client = HorizonClientSync(base_url=external_app_url, auth=app_oauth2_password)
    sync_client.authorize()
    assert sync_client.session.token
    assert isinstance(sync_client.session.token, AuthlibToken)


def test_sync_client_auth_access_token_auth(external_app_url: str, app_access_token: AccessToken):
    sync_client = HorizonClientSync(base_url=external_app_url, auth=app_access_token)
    sync_client.authorize()
    assert sync_client.session.token
    assert isinstance(sync_client.session.token, AuthlibToken)


def test_sync_client_auth_not_auccess(external_app_url: str, app_oauth2_password: OAuth2Password):
    app_oauth2_password.token_endpoint = external_app_url + "/v1/auth/wrong"
    sync_client = HorizonClientSync(base_url=external_app_url, auth=app_oauth2_password)

    with pytest.raises(UnsupportedTokenTypeError):
        sync_client.authorize()

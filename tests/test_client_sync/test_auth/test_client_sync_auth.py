# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from authlib.oauth2.auth import OAuth2Token as AuthlibToken

from horizon.client.auth import AccessToken, LoginPassword
from horizon.client.client.sync import HorizonClientSync


def test_sync_client_auth_login_password(external_app_url: str, app_login_password: LoginPassword):
    sync_client = HorizonClientSync(base_url=external_app_url, auth=app_login_password)
    sync_client.authorize()
    assert sync_client.session.token
    assert isinstance(sync_client.session.token, AuthlibToken)


def test_sync_client_auth_access_token_auth(external_app_url: str, app_access_token: AccessToken):
    sync_client = HorizonClientSync(base_url=external_app_url, auth=app_access_token)
    sync_client.authorize()
    assert sync_client.session.token
    assert isinstance(sync_client.session.token, AuthlibToken)

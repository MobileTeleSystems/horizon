from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import responses
from authlib.integrations.base_client.errors import OAuthError
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.auth import OAuth2Token as AuthlibToken
from pytest_lazyfixture import lazy_fixture
from requests.exceptions import ConnectionError, RetryError
from urllib3 import __version__ as urllib3_version
from urllib3.exceptions import ReadTimeoutError

from horizon.client.auth import AccessToken, LoginPassword
from horizon.client.sync import HorizonClientSync, RetryConfig, TimeoutConfig
from horizon.commons.exceptions.auth import AuthorizationError

if TYPE_CHECKING:
    from horizon.backend.db.models import User

pytestmark = [pytest.mark.client_sync, pytest.mark.client, pytest.mark.auth]


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as r:
        yield r


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


@pytest.mark.parametrize(
    ["retry_config", "use_custom_session"],
    [
        (RetryConfig(total=4, backoff_factor=1, status_forcelist=[503, 504], backoff_jitter=0.2), False),
        (RetryConfig(total=4, backoff_factor=1, status_forcelist=[503, 504], backoff_jitter=0.2), True),
        (RetryConfig(), False),  # test default retry
    ],
)
def test_sync_client_retry(
    external_app_url: str,
    user: User,
    mocked_responses: responses.RequestsMock,
    retry_config: RetryConfig,
    use_custom_session: bool,
):
    if retry_config.backoff_jitter is not None and urllib3_version.startswith("1."):
        pytest.skip(reason="urllib3 1.x does not support backoff_jitter")

    session = OAuth2Session() if use_custom_session else None
    if use_custom_session:
        session.headers.update({"Custom-Header": "HeaderValue"})
        session.cookies.set("session_cookie", "cookie_value")
        session.timeout = 30

    client = HorizonClientSync(
        base_url=external_app_url,
        auth=LoginPassword(login=user.username, password="test"),
        retry=retry_config,
        session=session,
    )

    # mock the POST request to /v1/auth/token for failures
    for _ in range(client.retry.total - 1):
        mocked_responses.add(
            responses.POST,
            f"{external_app_url}/v1/auth/token",
            json={"access_token": "valid-token", "token_type": "bearer"},
            status=503,
        )

    # mock successful POST request to /v1/auth/token
    mocked_responses.add(
        responses.POST,
        f"{external_app_url}/v1/auth/token",
        json={"access_token": "valid-token", "token_type": "bearer"},
        status=200,
    )

    # client.authorize() also calls /v1/users/me endpoint, so we need to mock it either
    mocked_responses.add(
        responses.GET,
        f"{external_app_url}/v1/users/me",
        json={"id": "1", "username": "user"},
        status=200,
    )

    client.authorize()
    assert client.session.token["access_token"] == "valid-token"


def test_sync_client_retry_max_attempts_error(
    external_app_url: str,
    user: User,
    mocked_responses: responses.RequestsMock,
):
    retry_config = RetryConfig(total=4, backoff_factor=1, status_forcelist=[503, 504])
    client = HorizonClientSync(
        base_url=external_app_url,
        auth=LoginPassword(login=user.username, password="test"),
        retry=retry_config,
    )

    # mock unsuccessful POST requests to /v1/auth/token more than total retries
    for _ in range(retry_config.total + 1):
        mocked_responses.add(
            responses.POST,
            f"{external_app_url}/v1/auth/token",
            json={"error": "Server Error"},
            status=503,
        )

    with pytest.raises(RetryError, match="Max retries exceeded with url:"):
        client.authorize()


def test_sync_client_retry_unhandled_code_error(
    external_app_url: str,
    user: User,
    mocked_responses: responses.RequestsMock,
):
    retry_config = RetryConfig(total=4, backoff_factor=1, status_forcelist=[503, 504])
    client = HorizonClientSync(
        base_url=external_app_url,
        auth=LoginPassword(login=user.username, password="test"),
        retry=retry_config,
    )

    # mock unsuccessful POST requests to /v1/auth/token m that unhandled with retry config (there are not retries)
    mocked_responses.add(
        responses.POST,
        f"{external_app_url}/v1/auth/token",
        json={"error": "Fails with first request"},
        status=407,
    )

    with pytest.raises(OAuthError, match="Fails with first request"):
        client.authorize()


@pytest.mark.flaky(reruns=5)
def test_sync_client_timeout_error(external_app_url: str, user: User):
    timeout_config = TimeoutConfig(request_timeout=0.000001)

    client = HorizonClientSync(
        base_url=external_app_url,
        auth=LoginPassword(login=user.username, password="test"),
        timeout=timeout_config,
    )

    with pytest.raises((ConnectionError, ReadTimeoutError)):
        client.authorize()

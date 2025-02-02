from __future__ import annotations

import pytest
from authlib.jose.errors import ExpiredTokenError, JoseError

from horizon.client.auth import AccessToken

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_access_token_constructor_expired(access_token_expired: AccessToken):
    with pytest.raises(ExpiredTokenError):
        AccessToken(token=access_token_expired)


def test_access_token_constructor_no_expiration_time(access_token_no_expiration_time: AccessToken):
    with pytest.raises(ExpiredTokenError):
        AccessToken(token=access_token_no_expiration_time)


def test_access_token_constructor_malformed(access_token_malformed: AccessToken):
    with pytest.raises(JoseError):
        AccessToken(token=access_token_malformed)

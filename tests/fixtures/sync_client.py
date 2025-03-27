from collections.abc import Generator

import pytest

from horizon.client.auth import AccessToken
from horizon.client.sync import HorizonClientSync


@pytest.fixture
def sync_client(access_token: str, external_app_url: str) -> Generator[HorizonClientSync, None, None]:
    with HorizonClientSync(base_url=external_app_url, auth=AccessToken(token=access_token)) as client:
        yield client

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from collections.abc import Generator

import pytest

from horizon_client.auth import AccessToken
from horizon_client.client.sync import HorizonClientSync


@pytest.mark.client
@pytest.mark.client_sync
@pytest.fixture
def sync_client(access_token: str, external_app_url: str) -> Generator[HorizonClientSync, None, None]:
    with HorizonClientSync(base_url=external_app_url, auth=AccessToken(token=access_token)) as client:
        yield client

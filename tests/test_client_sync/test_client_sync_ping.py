# SPDX-FileCopyrightText: 2023 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import pytest

from horizon.client.sync import HorizonClientSync
from horizon.commons.schemas import PingResponse

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_ping(sync_client: HorizonClientSync):
    assert sync_client.ping() == PingResponse(status="ok")

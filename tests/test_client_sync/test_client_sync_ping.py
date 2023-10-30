# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from horizon_client.client.sync import HorizonClientSync
from horizon_commons.schemas import PingResponse


def test_sync_client_ping_route(sync_client: HorizonClientSync):
    assert sync_client.ping() == PingResponse(status="ok")

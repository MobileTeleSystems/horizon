# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from horizon.client.sync import HorizonClientSync
from horizon.commons.schemas import PingResponse


def test_sync_client_ping(sync_client: HorizonClientSync):
    assert sync_client.ping() == PingResponse(status="ok")

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.commons.schemas import PingResponse

if TYPE_CHECKING:
    from horizon.client.sync import HorizonClientSync

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_ping(sync_client: HorizonClientSync):
    assert sync_client.ping() == PingResponse(status="ok")

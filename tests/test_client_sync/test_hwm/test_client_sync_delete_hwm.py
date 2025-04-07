from __future__ import annotations

import re
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
import requests

from horizon.commons.exceptions.entity import EntityNotFoundError

if TYPE_CHECKING:
    from horizon.backend.db.models import HWM, Namespace
    from horizon.client.sync import HorizonClientSync

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_delete_hwm(hwm: HWM, sync_client: HorizonClientSync):
    response = sync_client.delete_hwm(hwm.id)
    assert response is None

    with pytest.raises(EntityNotFoundError):
        sync_client.get_hwm(hwm.id)


def test_sync_client_delete_hwm_missing(
    new_namespace: Namespace,
    new_hwm: HWM,
    sync_client: HorizonClientSync,
):
    with pytest.raises(
        EntityNotFoundError,
        match=re.escape(f"HWM with id={new_hwm.id!r} not found"),
    ) as e:
        sync_client.delete_hwm(new_hwm.id)

    assert e.value.details == {
        "entity_type": "HWM",
        "field": "id",
        "value": new_hwm.id,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == HTTPStatus.NOT_FOUND


def test_sync_client_delete_hwm_malformed(sync_client: HorizonClientSync):
    with pytest.raises(requests.exceptions.HTTPError, match="422 Client Error"):
        sync_client.delete_hwm("")

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from typing import TYPE_CHECKING, List

import pytest
import requests

from horizon.client.sync import HorizonClientSync
from horizon.commons.exceptions.entity import EntityNotFoundError

if TYPE_CHECKING:
    from horizon.backend.db.models import HWM, Namespace

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_bulk_delete_hwm(namespace: Namespace, hwms: List[HWM], sync_client: HorizonClientSync):
    hwm_ids = [hwm.id for hwm in hwms]
    response = sync_client.bulk_delete_hwm(namespace_id=namespace.id, hwm_ids=hwm_ids)
    assert response is None

    for hwm_id in hwm_ids:
        with pytest.raises(EntityNotFoundError):
            sync_client.get_hwm(hwm_id)


def test_sync_client_bulk_delete_hwm_missing(
    namespace: Namespace,
    hwm: HWM,
    new_hwm: HWM,
    sync_client: HorizonClientSync,
):
    with pytest.raises(
        EntityNotFoundError,
        match=re.escape(f"HWMs with ids=[{new_hwm.id!r}] not found"),
    ) as e:
        sync_client.bulk_delete_hwm(namespace_id=namespace.id, hwm_ids=[hwm.id, new_hwm.id])

    assert e.value.details == {
        "entity_type": "HWMs",
        "field": "ids",
        "value": [new_hwm.id],
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404


def test_sync_client_bulk_delete_hwm_malformed(sync_client: HorizonClientSync):
    with pytest.raises(ValueError):
        sync_client.bulk_delete_hwm("", "")

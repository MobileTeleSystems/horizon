# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING, List

import pytest

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
    sync_client.bulk_delete_hwm(namespace_id=namespace.id, hwm_ids=[hwm.id, new_hwm.id])

    # we ignore hwms that are not related to namespace and delete only existing hws in namespace
    with pytest.raises(EntityNotFoundError):
        sync_client.get_hwm(hwm.id)


def test_sync_client_bulk_delete_hwm_malformed(sync_client: HorizonClientSync):
    with pytest.raises(ValueError):
        sync_client.bulk_delete_hwm("", "")

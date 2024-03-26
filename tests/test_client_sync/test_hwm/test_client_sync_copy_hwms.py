# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.client.sync import HorizonClientSync
from horizon.commons.schemas.v1 import HWMCopyRequestV1

if TYPE_CHECKING:
    from horizon.backend.db.models import HWM, Namespace

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_copy_hwms(
    namespaces: list[Namespace],
    hwms: list[HWM],
    sync_client: HorizonClientSync,
):
    source_namespace = hwms[0].namespace
    target_namespace = namespaces[0]

    copy_request = HWMCopyRequestV1(
        source_namespace_id=source_namespace.id,
        target_namespace_id=target_namespace.id,
        hwm_ids=[hwm.id for hwm in hwms],
        with_history=False,
    )
    copied_hwms = sync_client.copy_hwms(copy_request)

    assert len(copied_hwms.hwms) == len(hwms)
    for original_hwm, copied_hwm in zip(hwms, copied_hwms.hwms):
        assert copied_hwm.name == original_hwm.name
        assert copied_hwm.namespace_id == target_namespace.id


def test_sync_client_copy_hwms_with_non_existing_ids(
    namespaces: list[Namespace],
    hwms: list[HWM],
    new_hwm: HWM,
    sync_client: HorizonClientSync,
):
    source_namespace = hwms[0].namespace
    target_namespace = namespaces[0]

    non_existing_id = new_hwm.id
    copy_request = HWMCopyRequestV1(
        source_namespace_id=source_namespace.id,
        target_namespace_id=target_namespace.id,
        hwm_ids=[hwm.id for hwm in hwms] + [non_existing_id],
        with_history=False,
    )
    copied_hwms = sync_client.copy_hwms(copy_request)

    assert len(copied_hwms.hwms) == len(hwms)


def test_sync_client_copy_hwms_malformed(sync_client: HorizonClientSync):
    with pytest.raises(AttributeError):
        sync_client.copy_hwms("")

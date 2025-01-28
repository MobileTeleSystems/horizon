from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.client.sync import HorizonClientSync
from horizon.commons.schemas.v1 import HWMBulkCopyRequestV1

if TYPE_CHECKING:
    from horizon.backend.db.models import HWM, Namespace

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_bulk_copy_hwm(
    namespaces: list[Namespace],
    hwms: list[HWM],
    sync_client: HorizonClientSync,
):
    source_namespace = hwms[0].namespace
    target_namespace = namespaces[0]
    hwm_ids = [hwm.id for hwm in hwms]

    copy_request = HWMBulkCopyRequestV1(
        source_namespace_id=source_namespace.id,
        target_namespace_id=target_namespace.id,
        hwm_ids=hwm_ids,
        with_history=False,
    )
    copied_hwms_response = sync_client.bulk_copy_hwm(copy_request)

    assert len(copied_hwms_response.hwms) == len(hwm_ids)

    original_hwms_by_name = {hwm.name: hwm for hwm in hwms}
    for copied_hwm in copied_hwms_response.hwms:
        original_hwm = original_hwms_by_name.get(copied_hwm.name)
        assert original_hwm is not None
        assert copied_hwm.name == original_hwm.name
        assert copied_hwm.namespace_id == target_namespace.id
        assert copied_hwm.description == original_hwm.description
        assert copied_hwm.type == original_hwm.type


def test_sync_client_bulk_copy_hwm_with_non_existing_ids(
    namespaces: list[Namespace],
    hwms: list[HWM],
    new_hwm: HWM,
    sync_client: HorizonClientSync,
):
    source_namespace = hwms[0].namespace
    target_namespace = namespaces[0]

    non_existing_id = new_hwm.id
    copy_request = HWMBulkCopyRequestV1(
        source_namespace_id=source_namespace.id,
        target_namespace_id=target_namespace.id,
        hwm_ids=[hwm.id for hwm in hwms] + [non_existing_id],
        with_history=False,
    )
    copied_hwms = sync_client.bulk_copy_hwm(copy_request)

    assert len(copied_hwms.hwms) == len(hwms)


def test_sync_client_bulk_copy_hwm_malformed(sync_client: HorizonClientSync):
    with pytest.raises(AttributeError):
        sync_client.bulk_copy_hwm("")

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.client.sync import HorizonClientSync
from horizon.commons.schemas.v1 import (
    HWMHistoryPaginateQueryV1,
    HWMHistoryResponseV1,
    PageMetaResponseV1,
    PageResponseV1,
)

if TYPE_CHECKING:
    from horizon.backend.db.models import HWM, HWMHistory

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_paginate_hwm_history(
    hwm: HWM,
    hwm_history_items: list[HWMHistory],
    sync_client: HorizonClientSync,
):
    hwm_history_items = sorted(hwm_history_items, key=lambda item: item.changed_at, reverse=True)
    items = [
        HWMHistoryResponseV1(
            id=item.id,
            hwm_id=item.hwm_id,
            namespace_id=item.namespace_id,
            name=item.name,
            type=item.type,
            value=item.value,
            entity=item.entity,
            expression=item.expression,
            description=item.description,
            changed_at=item.changed_at,
            changed_by=item.changed_by,
        )
        for item in hwm_history_items
    ]

    response = sync_client.paginate_hwm_history(HWMHistoryPaginateQueryV1(hwm_id=hwm.id))
    assert response == PageResponseV1[HWMHistoryResponseV1](
        meta=PageMetaResponseV1(
            page=1,
            pages_count=1,
            total_count=len(items),
            page_size=20,
            has_next=False,
            has_previous=False,
            next_page=None,
            previous_page=None,
        ),
        items=items,
    )


@pytest.mark.parametrize("hwm_history_items", [(10, {})], indirect=True)
def test_sync_client_paginate_hwm_history_page_options(
    hwm: HWM,
    hwm_history_items: list[HWMHistory],
    sync_client: HorizonClientSync,
):
    hwm_history_items = sorted(hwm_history_items, key=lambda item: item.changed_at, reverse=True)
    items = [
        HWMHistoryResponseV1(
            id=item.id,
            hwm_id=item.hwm_id,
            namespace_id=item.namespace_id,
            name=item.name,
            type=item.type,
            value=item.value,
            entity=item.entity,
            expression=item.expression,
            description=item.description,
            changed_at=item.changed_at,
            changed_by=item.changed_by,
        )
        for item in hwm_history_items
    ]

    page1 = sync_client.paginate_hwm_history(
        HWMHistoryPaginateQueryV1(hwm_id=hwm.id, page=1, page_size=8),
    )
    assert page1 == PageResponseV1[HWMHistoryResponseV1](
        meta=PageMetaResponseV1(
            page=1,
            pages_count=2,
            total_count=10,
            page_size=8,
            has_next=True,
            has_previous=False,
            next_page=2,
            previous_page=None,
        ),
        items=items[0:8],
    )

    page2 = sync_client.paginate_hwm_history(
        HWMHistoryPaginateQueryV1(hwm_id=hwm.id, page=2, page_size=8),
    )
    assert page2 == PageResponseV1[HWMHistoryResponseV1](
        meta=PageMetaResponseV1(
            page=2,
            pages_count=2,
            total_count=10,
            page_size=8,
            has_next=False,
            has_previous=True,
            next_page=None,
            previous_page=1,
        ),
        items=items[8:],
    )

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.client.sync import HorizonClientSync
from horizon.commons.schemas.v1 import (
    HWMPaginateQueryV1,
    HWMResponseV1,
    PageMetaResponseV1,
    PageResponseV1,
)

if TYPE_CHECKING:
    from horizon.backend.db.models import HWM, Namespace

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_paginate_hwm(namespace: Namespace, hwms: list[HWM], sync_client: HorizonClientSync):
    hwms = sorted(hwms, key=lambda item: item.name)
    items = [
        HWMResponseV1(
            id=hwm.id,
            namespace_id=hwm.namespace_id,
            name=hwm.name,
            type=hwm.type,
            value=hwm.value,
            entity=hwm.entity,
            expression=hwm.expression,
            description=hwm.description,
            changed_at=hwm.changed_at,
            changed_by=hwm.changed_by,
        )
        for hwm in hwms
    ]

    response = sync_client.paginate_hwm(HWMPaginateQueryV1(namespace_id=namespace.id))
    assert response == PageResponseV1[HWMResponseV1](
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


def test_sync_client_paginate_hwm_filter_by_name(namespace: Namespace, hwms: list[HWM], sync_client: HorizonClientSync):
    hwm = hwms[0]

    response = sync_client.paginate_hwm(HWMPaginateQueryV1(namespace_id=namespace.id, name=hwm.name))
    assert response == PageResponseV1[HWMResponseV1](
        meta=PageMetaResponseV1(
            page=1,
            pages_count=1,
            total_count=1,
            page_size=20,
            has_next=False,
            has_previous=False,
            next_page=None,
            previous_page=None,
        ),
        items=[
            HWMResponseV1(
                id=hwm.id,
                namespace_id=hwm.namespace_id,
                name=hwm.name,
                type=hwm.type,
                value=hwm.value,
                entity=hwm.entity,
                expression=hwm.expression,
                description=hwm.description,
                changed_at=hwm.changed_at,
                changed_by=hwm.changed_by,
            ),
        ],
    )


@pytest.mark.parametrize("hwms", [(10, {})], indirect=True)
def test_sync_client_paginate_hwm_page_options(
    namespace: Namespace,
    hwms: list[HWM],
    sync_client: HorizonClientSync,
):
    hwms = sorted(hwms, key=lambda item: item.name)
    items = [
        HWMResponseV1(
            id=hwm.id,
            namespace_id=hwm.namespace_id,
            name=hwm.name,
            type=hwm.type,
            value=hwm.value,
            entity=hwm.entity,
            expression=hwm.expression,
            description=hwm.description,
            changed_at=hwm.changed_at,
            changed_by=hwm.changed_by,
        )
        for hwm in hwms
    ]

    page1 = sync_client.paginate_hwm(HWMPaginateQueryV1(namespace_id=namespace.id, page=1, page_size=8))
    assert page1 == PageResponseV1[HWMResponseV1](
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

    page2 = sync_client.paginate_hwm(HWMPaginateQueryV1(namespace_id=namespace.id, page=2, page_size=8))
    assert page2 == PageResponseV1[HWMResponseV1](
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

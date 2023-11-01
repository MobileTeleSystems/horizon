# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import pytest

from horizon.db.models import HWM, Namespace, User
from horizon_client.client.sync import HorizonClientSync
from horizon_commons.schemas.v1 import (
    HWMPaginateQueryV1,
    HWMResponseV1,
    PageMetaResponseV1,
    PageResponseV1,
)


def test_sync_client_paginate_hwm(namespace: Namespace, hwms: list[HWM], sync_client: HorizonClientSync):
    hwms = sorted(hwms, key=lambda item: item.name)
    items = [
        HWMResponseV1(
            id=hwm.id,
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

    response = sync_client.paginate_hwm(namespace.name)
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


@pytest.mark.parametrize("hwms", [(10, {})], indirect=True)
def test_sync_client_paginate_hwm_with_params(
    namespace: Namespace,
    hwms: list[HWM],
    sync_client: HorizonClientSync,
):
    hwms = sorted(hwms, key=lambda item: item.name)
    items = [
        HWMResponseV1(
            id=hwm.id,
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

    page1 = sync_client.paginate_hwm(namespace.name, query=HWMPaginateQueryV1(page=1, page_size=8))
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

    page2 = sync_client.paginate_hwm(namespace.name, query=HWMPaginateQueryV1(page=2, page_size=8))
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

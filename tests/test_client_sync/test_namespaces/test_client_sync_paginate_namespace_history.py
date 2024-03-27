# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.client.sync import HorizonClientSync
from horizon.commons.schemas.v1 import (
    NamespaceHistoryPaginateQueryV1,
    NamespaceHistoryResponseV1,
    PageMetaResponseV1,
    PageResponseV1,
)

if TYPE_CHECKING:
    from horizon.backend.db.models import Namespace, NamespaceHistory

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_paginate_namespace_history(
    namespace: Namespace,
    namespace_history_items: list[NamespaceHistory],
    sync_client: HorizonClientSync,
):
    namespace_history_items = sorted(namespace_history_items, key=lambda item: item.changed_at, reverse=True)
    items = [
        NamespaceHistoryResponseV1(
            id=item.id,
            namespace_id=item.namespace_id,
            name=item.name,
            description=item.description,
            action=item.action,
            changed_at=item.changed_at,
            changed_by=item.changed_by,
            owned_by=item.owned_by,
        )
        for item in namespace_history_items
    ]

    response = sync_client.paginate_namespace_history(NamespaceHistoryPaginateQueryV1(namespace_id=namespace.id))
    assert response == PageResponseV1[NamespaceHistoryResponseV1](
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


@pytest.mark.parametrize("namespace_history_items", [(10, {})], indirect=True)
def test_sync_client_paginate_namespace_history_page_options(
    namespace: Namespace,
    namespace_history_items: list[NamespaceHistory],
    sync_client: HorizonClientSync,
):
    namespace_history_items = sorted(namespace_history_items, key=lambda item: item.changed_at, reverse=True)
    items = [
        NamespaceHistoryResponseV1(
            id=item.id,
            namespace_id=item.namespace_id,
            name=item.name,
            description=item.description,
            changed_at=item.changed_at,
            changed_by=item.changed_by,
            owned_by=item.owned_by,
            action=item.action,
        )
        for item in namespace_history_items
    ]

    page1 = sync_client.paginate_namespace_history(
        NamespaceHistoryPaginateQueryV1(namespace_id=namespace.id, page=1, page_size=8),
    )
    assert page1 == PageResponseV1[NamespaceHistoryResponseV1](
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
        items=items[:8],
    )

    page2 = sync_client.paginate_namespace_history(
        NamespaceHistoryPaginateQueryV1(namespace_id=namespace.id, page=2, page_size=8),
    )
    assert page2 == PageResponseV1[NamespaceHistoryResponseV1](
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

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.client.sync import HorizonClientSync
from horizon.commons.schemas.v1 import (
    NamespacePaginateQueryV1,
    NamespaceResponseV1,
    PageMetaResponseV1,
    PageResponseV1,
)

if TYPE_CHECKING:
    from horizon.backend.db.models import Namespace

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_paginate_namespaces(namespaces: list[Namespace], sync_client: HorizonClientSync):
    namespaces = sorted(namespaces, key=lambda item: item.name)
    items = [
        NamespaceResponseV1(
            id=namespace.id,
            name=namespace.name,
            description=namespace.description,
            changed_at=namespace.changed_at,
            changed_by=namespace.changed_by,
            owned_by=namespace.owned_by,
        )
        for namespace in namespaces
    ]

    response = sync_client.paginate_namespaces()
    assert response == PageResponseV1[NamespaceResponseV1](
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


def test_sync_client_paginate_namespaces_filter_by_name(namespaces: list[Namespace], sync_client: HorizonClientSync):
    namespace = namespaces[0]

    response = sync_client.paginate_namespaces(NamespacePaginateQueryV1(name=namespace.name))
    assert response == PageResponseV1[NamespaceResponseV1](
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
            NamespaceResponseV1(
                id=namespace.id,
                name=namespace.name,
                description=namespace.description,
                changed_at=namespace.changed_at,
                changed_by=namespace.changed_by,
                owned_by=namespace.owned_by,
            ),
        ],
    )


@pytest.mark.parametrize("namespaces", [(10, {})], indirect=True)
def test_sync_client_paginate_namespaces_page_options(
    namespaces: list[Namespace],
    sync_client: HorizonClientSync,
):
    namespaces = sorted(namespaces, key=lambda item: item.name)
    items = [
        NamespaceResponseV1(
            id=namespace.id,
            name=namespace.name,
            description=namespace.description,
            changed_at=namespace.changed_at,
            changed_by=namespace.changed_by,
            owned_by=namespace.owned_by,
        )
        for namespace in namespaces
    ]

    page1 = sync_client.paginate_namespaces(NamespacePaginateQueryV1(page=1, page_size=8))
    assert page1 == PageResponseV1[NamespaceResponseV1](
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

    page2 = sync_client.paginate_namespaces(NamespacePaginateQueryV1(page=2, page_size=8))
    assert page2 == PageResponseV1[NamespaceResponseV1](
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

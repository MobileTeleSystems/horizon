# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import pytest

from horizon.db.models import Namespace, User
from horizon_client.client.sync import HorizonClientSync
from horizon_commons.schemas.v1 import (
    NamespacePaginateQueryV1,
    NamespaceResponseV1,
    PageMetaResponseV1,
    PageResponseV1,
)


def test_sync_client_paginate_namespaces(namespaces: list[Namespace], user: User, sync_client: HorizonClientSync):
    namespaces = sorted(namespaces, key=lambda item: item.name)
    items = [
        NamespaceResponseV1(
            id=namespace.id,
            name=namespace.name,
            description=namespace.description,
            changed_at=namespace.changed_at,
            changed_by=user.username,
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


@pytest.mark.parametrize("namespaces", [(10, {})], indirect=True)
def test_sync_client_paginate_namespaces_with_params(
    namespaces: list[Namespace],
    user: User,
    sync_client: HorizonClientSync,
):
    namespaces = sorted(namespaces, key=lambda item: item.name)
    items = [
        NamespaceResponseV1(
            id=namespace.id,
            name=namespace.name,
            description=namespace.description,
            changed_at=namespace.changed_at,
            changed_by=user.username,
        )
        for namespace in namespaces
    ]

    page1 = sync_client.paginate_namespaces(query=NamespacePaginateQueryV1(page=1, page_size=8))
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

    page2 = sync_client.paginate_namespaces(query=NamespacePaginateQueryV1(page=2, page_size=8))
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

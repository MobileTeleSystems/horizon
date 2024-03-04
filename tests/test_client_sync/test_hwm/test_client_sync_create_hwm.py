# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
import requests

from horizon.client.sync import HorizonClientSync
from horizon.commons.exceptions.entity import EntityNotFoundError
from horizon.commons.schemas.v1 import HWMCreateRequestV1, HWMResponseV1

if TYPE_CHECKING:
    from horizon.backend.db.models import HWM, Namespace, User

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_create_hwm_create_new_full(
    namespace: Namespace,
    new_hwm: HWM,
    user: User,
    sync_client: HorizonClientSync,
):
    to_create = HWMCreateRequestV1(
        namespace_id=namespace.id,
        name=new_hwm.name,
        type=new_hwm.type,
        value=new_hwm.value,
        entity=new_hwm.entity,
        expression=new_hwm.expression,
        description=new_hwm.description,
    )
    response = sync_client.create_hwm(to_create)

    assert isinstance(response, HWMResponseV1)
    assert response.dict(exclude={"id", "changed_at"}) == dict(
        namespace_id=namespace.id,
        name=new_hwm.name,
        type=new_hwm.type,
        value=new_hwm.value,
        entity=new_hwm.entity,
        expression=new_hwm.expression,
        description=new_hwm.description,
        changed_by=user.username,
    )


def test_sync_client_create_hwm_create_new_minimal(
    namespace: Namespace,
    new_hwm: HWM,
    user: User,
    sync_client: HorizonClientSync,
):
    to_create = HWMCreateRequestV1(
        namespace_id=namespace.id,
        name=new_hwm.name,
        type=new_hwm.type,
        value=new_hwm.value,
    )
    response = sync_client.create_hwm(to_create)

    assert isinstance(response, HWMResponseV1)
    assert response.dict(exclude={"id", "changed_at"}) == dict(
        namespace_id=namespace.id,
        name=new_hwm.name,
        type=new_hwm.type,
        value=new_hwm.value,
        entity=None,
        expression=None,
        description="",
        changed_by=user.username,
    )


def test_sync_client_create_hwm_namespace_missing(
    new_namespace: Namespace,
    new_hwm: HWM,
    sync_client: HorizonClientSync,
):
    to_create = HWMCreateRequestV1(
        namespace_id=new_namespace.id,
        name=new_hwm.name,
        type=new_hwm.type,
        value=new_hwm.value,
        entity=new_hwm.entity,
        expression=new_hwm.expression,
        description=new_hwm.description,
    )

    with pytest.raises(
        EntityNotFoundError,
        match=re.escape(f"Namespace with owner_id={new_namespace.owner_id!r} not found"),
    ) as e:
        sync_client.create_hwm(to_create)

    assert e.value.details == {
        "entity_type": "Namespace",
        "field": "owner_id",
        "value": new_namespace.owner_id,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import pytest
import requests

from horizon.db.models import HWM, Namespace, User
from horizon_client.client.sync import HorizonClientSync
from horizon_commons.exceptions.entity import EntityNotFoundError
from horizon_commons.schemas.v1 import HWMResponseV1, HWMWriteRequestV1


def test_sync_client_write_hwm_create_new_full(
    namespace: Namespace,
    new_hwm: HWM,
    user: User,
    sync_client: HorizonClientSync,
):
    to_write = HWMWriteRequestV1(
        type=new_hwm.type,
        value=new_hwm.value,
        entity=new_hwm.entity,
        expression=new_hwm.expression,
        description=new_hwm.description,
    )
    response = sync_client.write_hwm(namespace.name, new_hwm.name, to_write)

    assert isinstance(response, HWMResponseV1)
    assert response.dict(exclude={"id", "changed_at"}) == dict(
        name=new_hwm.name,
        type=new_hwm.type,
        value=new_hwm.value,
        entity=new_hwm.entity,
        expression=new_hwm.expression,
        description=new_hwm.description,
        changed_by=user.username,
    )


def test_sync_client_write_hwm_create_new_minimal(
    namespace: Namespace,
    new_hwm: HWM,
    user: User,
    sync_client: HorizonClientSync,
):
    to_write = HWMWriteRequestV1(
        type=new_hwm.type,
        value=new_hwm.value,
    )
    response = sync_client.write_hwm(namespace.name, new_hwm.name, to_write)

    assert isinstance(response, HWMResponseV1)
    assert response.dict(exclude={"id", "changed_at"}) == dict(
        name=new_hwm.name,
        type=new_hwm.type,
        value=new_hwm.value,
        entity=None,
        expression=None,
        description="",
        changed_by=user.username,
    )


def test_sync_client_write_hwm_update_existing_full(
    namespace: Namespace,
    new_hwm: HWM,
    hwm: HWM,
    user: User,
    sync_client: HorizonClientSync,
):
    to_write = HWMWriteRequestV1(
        type=new_hwm.type,
        value=new_hwm.value,
        entity=new_hwm.entity,
        expression=new_hwm.expression,
        description=new_hwm.description,
    )
    response = sync_client.write_hwm(namespace.name, hwm.name, to_write)

    assert isinstance(response, HWMResponseV1)
    assert response.dict(exclude={"id", "changed_at"}) == dict(
        name=hwm.name,
        type=new_hwm.type,
        value=new_hwm.value,
        entity=new_hwm.entity,
        expression=new_hwm.expression,
        description=new_hwm.description,
        changed_by=user.username,
    )


def test_sync_client_write_hwm_update_existing_minimal(
    namespace: Namespace,
    new_hwm: HWM,
    hwm: HWM,
    user: User,
    sync_client: HorizonClientSync,
):
    to_write = HWMWriteRequestV1(value=new_hwm.value)
    response = sync_client.write_hwm(namespace.name, hwm.name, to_write)

    assert isinstance(response, HWMResponseV1)
    assert response.dict(exclude={"id", "changed_at"}) == dict(
        name=hwm.name,
        type=hwm.type,
        value=new_hwm.value,
        entity=hwm.entity,
        expression=hwm.expression,
        description=hwm.description,
        changed_by=user.username,
    )


def test_sync_client_write_hwm_namespace_missing(
    new_namespace: Namespace,
    new_hwm: HWM,
    sync_client: HorizonClientSync,
):
    to_write = HWMWriteRequestV1(
        type=new_hwm.type,
        value=new_hwm.value,
        entity=new_hwm.entity,
        expression=new_hwm.expression,
        description=new_hwm.description,
    )

    with pytest.raises(EntityNotFoundError, match=f"Namespace with name='{new_namespace.name}' not found") as e:
        sync_client.write_hwm(new_namespace.name, new_hwm.name, to_write)

    assert e.value.details == {
        "entity_type": "Namespace",
        "field": "name",
        "value": new_namespace.name,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404


def test_sync_client_write_hwm_malformed(namespace: Namespace, new_hwm: HWM, sync_client: HorizonClientSync):
    to_write = HWMWriteRequestV1(
        type=new_hwm.type,
        value=new_hwm.value,
        entity=new_hwm.entity,
        expression=new_hwm.expression,
        description=new_hwm.description,
    )

    with pytest.raises(requests.exceptions.HTTPError, match="405 Client Error: Method Not Allowed for url"):
        sync_client.write_hwm(namespace.name, "", to_write)

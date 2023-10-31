# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import pytest
import requests

from horizon.db.models import Namespace, User
from horizon_client.client.sync import HorizonClientSync
from horizon_commons.exceptions.entity import EntityNotFoundError
from horizon_commons.schemas.v1 import NamespaceResponseV1, NamespaceUpdateRequestV1


def test_sync_client_update_namespace_name(
    namespace: Namespace,
    new_namespace: Namespace,
    user: User,
    sync_client: HorizonClientSync,
):
    to_update = NamespaceUpdateRequestV1(name=new_namespace.name)
    response = sync_client.update_namespace(namespace.name, to_update)

    assert isinstance(response, NamespaceResponseV1)
    assert response.dict(exclude={"changed_at"}) == dict(
        id=namespace.id,
        name=new_namespace.name,
        description=namespace.description,
        changed_by=user.username,
    )


def test_sync_client_update_namespace_description(
    namespace: Namespace,
    new_namespace: Namespace,
    user: User,
    sync_client: HorizonClientSync,
):
    to_update = NamespaceUpdateRequestV1(description=new_namespace.description)
    response = sync_client.update_namespace(namespace.name, to_update)

    assert isinstance(response, NamespaceResponseV1)
    assert response.dict(exclude={"changed_at"}) == dict(
        id=namespace.id,
        name=namespace.name,
        description=new_namespace.description,
        changed_by=user.username,
    )


def test_sync_client_update_namespace_missing(new_namespace: Namespace, sync_client: HorizonClientSync):
    to_update = NamespaceUpdateRequestV1(name=new_namespace.name, description=new_namespace.description)

    with pytest.raises(EntityNotFoundError, match=f"Namespace with name='{new_namespace.name}' not found") as e:
        sync_client.update_namespace(new_namespace.name, to_update)

    assert e.value.details == {
        "entity_type": "Namespace",
        "field": "name",
        "value": new_namespace.name,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404


def test_sync_client_update_namespace_malformed(new_namespace: Namespace, sync_client: HorizonClientSync):
    to_update = NamespaceUpdateRequestV1(name=new_namespace.name, description=new_namespace.description)

    with pytest.raises(requests.exceptions.HTTPError, match="405 Client Error: Method Not Allowed for url"):
        sync_client.update_namespace("", to_update)

from __future__ import annotations

import re
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
import requests

from horizon.commons.exceptions.entity import EntityNotFoundError
from horizon.commons.schemas.v1 import NamespaceResponseV1, NamespaceUpdateRequestV1

if TYPE_CHECKING:
    from horizon.backend.db.models import Namespace, User
    from horizon.client.sync import HorizonClientSync

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_update_namespace_name(
    namespace: Namespace,
    new_namespace: Namespace,
    user: User,
    sync_client: HorizonClientSync,
):
    to_update = NamespaceUpdateRequestV1(name=new_namespace.name)
    response = sync_client.update_namespace(namespace.id, to_update)

    assert isinstance(response, NamespaceResponseV1)
    assert response.dict(exclude={"changed_at"}) == {
        "id": namespace.id,
        "name": new_namespace.name,
        "description": namespace.description,
        "changed_by": user.username,
        "owned_by": user.username,
    }


def test_sync_client_update_namespace_description(
    namespace: Namespace,
    new_namespace: Namespace,
    user: User,
    sync_client: HorizonClientSync,
):
    to_update = NamespaceUpdateRequestV1(description=new_namespace.description)
    response = sync_client.update_namespace(namespace.id, to_update)

    assert isinstance(response, NamespaceResponseV1)
    assert response.dict(exclude={"changed_at"}) == {
        "id": namespace.id,
        "name": namespace.name,
        "description": new_namespace.description,
        "changed_by": user.username,
        "owned_by": user.username,
    }


def test_sync_client_update_namespace_missing(new_namespace: Namespace, sync_client: HorizonClientSync):
    to_update = NamespaceUpdateRequestV1(name=new_namespace.name, description=new_namespace.description)

    with pytest.raises(
        EntityNotFoundError,
        match=re.escape(f"Namespace with id={new_namespace.id!r} not found"),
    ) as e:
        sync_client.update_namespace(new_namespace.id, to_update)

    assert e.value.details == {
        "entity_type": "Namespace",
        "field": "id",
        "value": new_namespace.id,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == HTTPStatus.NOT_FOUND


def test_sync_client_update_namespace_malformed(new_namespace: Namespace, sync_client: HorizonClientSync):
    to_update = NamespaceUpdateRequestV1(name=new_namespace.name, description=new_namespace.description)

    with pytest.raises(requests.exceptions.HTTPError, match="405 Client Error: Method Not Allowed for url"):
        sync_client.update_namespace("", to_update)

from __future__ import annotations

import re
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
import requests

from horizon.commons.exceptions import EntityAlreadyExistsError
from horizon.commons.schemas.v1 import NamespaceCreateRequestV1, NamespaceResponseV1

if TYPE_CHECKING:
    from horizon.backend.db.models import Namespace, User
    from horizon.client.sync import HorizonClientSync

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_create_namespace(new_namespace: Namespace, user: User, sync_client: HorizonClientSync):
    to_create = NamespaceCreateRequestV1(
        name=new_namespace.name,
        description=new_namespace.description,
        owner_id=user.id,
    )
    response = sync_client.create_namespace(to_create)

    assert isinstance(response, NamespaceResponseV1)
    assert response.dict(exclude={"id", "changed_at"}) == {
        "name": to_create.name,
        "description": to_create.description,
        "changed_by": user.username,
        "owned_by": user.username,
    }


def test_sync_client_create_namespace_already_exists(namespace: Namespace, sync_client: HorizonClientSync):
    to_create = NamespaceCreateRequestV1(name=namespace.name, description="abc")
    with pytest.raises(
        EntityAlreadyExistsError,
        match=re.escape(f"Namespace with name={namespace.name!r} already exists"),
    ) as e:
        sync_client.create_namespace(to_create)

    assert e.value.details == {
        "entity_type": "Namespace",
        "field": "name",
        "value": namespace.name,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == HTTPStatus.CONFLICT

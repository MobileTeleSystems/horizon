from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pydantic
import pytest
import requests

from horizon.client.sync import HorizonClientSync
from horizon.commons.exceptions.entity import EntityNotFoundError
from horizon.commons.schemas.v1 import NamespaceResponseV1

if TYPE_CHECKING:
    from horizon.backend.db.models import Namespace

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_get_namespace(namespace: Namespace, sync_client: HorizonClientSync):
    response = sync_client.get_namespace(namespace.id)
    assert response == NamespaceResponseV1(
        id=namespace.id,
        name=namespace.name,
        description=namespace.description,
        changed_at=namespace.changed_at,
        changed_by=namespace.changed_by,
        owned_by=namespace.owned_by,
    )


def test_sync_client_get_namespace_missing(new_namespace: Namespace, sync_client: HorizonClientSync):
    with pytest.raises(
        EntityNotFoundError,
        match=re.escape(f"Namespace with id={new_namespace.id!r} not found"),
    ) as e:
        sync_client.get_namespace(new_namespace.id)

    assert e.value.details == {
        "entity_type": "Namespace",
        "field": "id",
        "value": new_namespace.id,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404


def test_sync_client_get_namespace_with_wrong_params(sync_client: HorizonClientSync):
    with pytest.raises(pydantic.ValidationError) as e:
        sync_client.get_namespace("")

    # exception with response body is attached as reason
    assert isinstance(e.value.__cause__, ValueError)
    assert e.value.__cause__.args[0] == {
        "items": [],
        "meta": {
            "has_next": False,
            "has_previous": False,
            "next_page": None,
            "page": 1,
            "page_size": 20,
            "pages_count": 1,
            "previous_page": None,
            "total_count": 0,
        },
    }

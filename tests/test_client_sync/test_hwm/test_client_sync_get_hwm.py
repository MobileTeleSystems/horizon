# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

import pydantic
import pytest
import requests

from horizon.client.sync import HorizonClientSync
from horizon.commons.exceptions.entity import EntityNotFoundError
from horizon.commons.schemas.v1 import HWMResponseV1

if TYPE_CHECKING:
    from horizon.backend.db.models import HWM, Namespace


def test_sync_client_get_hwm(namespace: Namespace, hwm: HWM, sync_client: HorizonClientSync):
    response = sync_client.get_hwm(namespace.name, hwm.name)
    assert response == HWMResponseV1(
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


def test_sync_client_get_hwm_namespace_missing(new_namespace: Namespace, new_hwm: HWM, sync_client: HorizonClientSync):
    with pytest.raises(EntityNotFoundError, match=f"Namespace with name='{new_namespace.name}' not found") as e:
        sync_client.get_hwm(new_namespace.name, new_hwm.name)

    assert e.value.details == {
        "entity_type": "Namespace",
        "field": "name",
        "value": new_namespace.name,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404


def test_sync_client_get_hwm_missing(namespace: Namespace, new_hwm: HWM, sync_client: HorizonClientSync):
    with pytest.raises(EntityNotFoundError, match=f"HWM with name='{new_hwm.name}' not found") as e:
        sync_client.get_hwm(namespace.name, new_hwm.name)

    assert e.value.details == {
        "entity_type": "HWM",
        "field": "name",
        "value": new_hwm.name,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404


def test_sync_client_get_hwm_with_wrong_params(namespace: Namespace, sync_client: HorizonClientSync):
    with pytest.raises(pydantic.ValidationError) as e:
        sync_client.get_hwm(namespace.name, "")

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

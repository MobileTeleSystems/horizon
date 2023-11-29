# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
import requests

from horizon.client.sync import HorizonClientSync
from horizon.commons.exceptions.entity import EntityNotFoundError

if TYPE_CHECKING:
    from horizon.backend.db.models import HWM, Namespace

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_delete_hwm(namespace: Namespace, hwm: HWM, sync_client: HorizonClientSync):
    response = sync_client.delete_hwm(namespace.name, hwm.name)
    assert response is None

    with pytest.raises(EntityNotFoundError):
        sync_client.get_hwm(namespace.name, hwm.name)


def test_sync_client_delete_hwm_namespace_missing(
    new_namespace: Namespace,
    new_hwm: HWM,
    sync_client: HorizonClientSync,
):
    with pytest.raises(EntityNotFoundError, match=f"Namespace with name='{new_namespace.name}' not found") as e:
        sync_client.delete_hwm(new_namespace.name, new_hwm.name)

    assert e.value.details == {
        "entity_type": "Namespace",
        "field": "name",
        "value": new_namespace.name,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404


def test_sync_client_delete_hwm_missing(namespace: Namespace, new_hwm: HWM, sync_client: HorizonClientSync):
    with pytest.raises(EntityNotFoundError, match=f"HWM with name='{new_hwm.name}' not found") as e:
        sync_client.delete_hwm(namespace.name, new_hwm.name)

    assert e.value.details == {
        "entity_type": "HWM",
        "field": "name",
        "value": new_hwm.name,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404


def test_sync_client_delete_hwm_malformed(new_namespace: Namespace, sync_client: HorizonClientSync):
    with pytest.raises(requests.exceptions.HTTPError, match="405 Client Error: Method Not Allowed for url"):
        sync_client.delete_hwm(new_namespace.name, "")

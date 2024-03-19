# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re

import pytest
import requests

from horizon.backend.db.models import Namespace, User
from horizon.client.sync import HorizonClientSync
from horizon.commons.dto import Role
from horizon.commons.exceptions.entity import EntityNotFoundError
from horizon.commons.schemas.v1 import PermissionResponseItemV1, PermissionsResponseV1

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_get_namespace_permissions(namespace: Namespace, user: User, sync_client: HorizonClientSync):
    response = sync_client.get_namespace_permissions(namespace.id)
    assert response == PermissionsResponseV1(
        permissions=[PermissionResponseItemV1(username=user.username, role=Role.OWNER)],
    )


def test_sync_client_get_namespace_permissions_missing(new_namespace: Namespace, sync_client: HorizonClientSync):
    with pytest.raises(
        EntityNotFoundError,
        match=re.escape(f"Namespace with id={new_namespace.id!r} not found"),
    ) as e:
        sync_client.get_namespace_permissions(new_namespace.id)

    assert e.value.details == {
        "entity_type": "Namespace",
        "field": "id",
        "value": new_namespace.id,
    }

    # original HTTP exception is attached as reason
    assert isinstance(e.value.__cause__, requests.exceptions.HTTPError)
    assert e.value.__cause__.response.status_code == 404

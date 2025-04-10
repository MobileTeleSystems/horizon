from __future__ import annotations

import re
from http import HTTPStatus
from typing import TYPE_CHECKING

import pytest
import requests

from horizon.backend.db.models import Namespace, NamespaceUserRoleInt, User
from horizon.commons.exceptions import EntityNotFoundError
from horizon.commons.schemas.v1 import (
    NamespaceUserRole,
    PermissionsResponseV1,
    PermissionsUpdateRequestV1,
    PermissionUpdateRequestItemV1,
)

if TYPE_CHECKING:
    from horizon.client.sync import HorizonClientSync

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


@pytest.mark.parametrize(
    "namespace_with_users",
    [
        [("new_user", NamespaceUserRoleInt.MAINTAINER)],
    ],
    indirect=["namespace_with_users"],
)
def test_sync_client_update_namespace_permissions(
    namespace: Namespace,
    user: User,
    sync_client: HorizonClientSync,
    namespace_with_users: None,
):
    changes = PermissionsUpdateRequestV1(
        permissions=[
            PermissionUpdateRequestItemV1(username=user.username, role=NamespaceUserRole.DEVELOPER),
            PermissionUpdateRequestItemV1(username="new_user", role=NamespaceUserRole.OWNER),
        ],
    )
    response = sync_client.update_namespace_permissions(namespace.id, changes)

    assert isinstance(response, PermissionsResponseV1)
    assert any(
        perm.username == user.username and perm.role == NamespaceUserRole.DEVELOPER for perm in response.permissions
    )
    assert any(perm.username == "new_user" and perm.role == NamespaceUserRole.OWNER for perm in response.permissions)


def test_sync_client_update_namespace_permissions_namespace_missing(
    new_namespace: Namespace,
    sync_client: HorizonClientSync,
):
    changes = PermissionsUpdateRequestV1(
        permissions=[
            PermissionUpdateRequestItemV1(username="someuser", role=NamespaceUserRole.DEVELOPER),
        ],
    )
    with pytest.raises(
        EntityNotFoundError,
        match=re.escape(f"Namespace with id={new_namespace.id!r} not found"),
    ) as exc_info:
        sync_client.update_namespace_permissions(new_namespace.id, changes)

    assert isinstance(exc_info.value.__cause__, requests.exceptions.HTTPError)
    assert exc_info.value.__cause__.response.status_code == HTTPStatus.NOT_FOUND

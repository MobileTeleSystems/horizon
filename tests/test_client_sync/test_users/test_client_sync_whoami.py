from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.backend.db.models import NamespaceUserRoleInt, User
from horizon.commons.schemas.v1 import UserResponseV1, UserResponseV1WithAdmin

if TYPE_CHECKING:
    from horizon.client.sync import HorizonClientSync

pytestmark = [pytest.mark.client_sync, pytest.mark.client]


def test_sync_client_whoami(sync_client: HorizonClientSync, user: User):
    assert sync_client.whoami() == UserResponseV1(
        id=user.id,
        username=user.username,
    )


@pytest.mark.parametrize(
    "user_with_role",
    [
        NamespaceUserRoleInt.SUPERADMIN,
    ],
    indirect=["user_with_role"],
)
def test_sync_client_whoami_superadmin(sync_client: HorizonClientSync, user: User, user_with_role: None):
    assert sync_client.whoami() == UserResponseV1WithAdmin(
        id=user.id,
        username=user.username,
        is_admin=user.is_admin,
    )

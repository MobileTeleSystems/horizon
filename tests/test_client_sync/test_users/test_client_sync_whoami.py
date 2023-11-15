# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from horizon.backend.db.models import User
from horizon.client.sync import HorizonClientSync
from horizon.commons.schemas.v1 import UserResponseV1


def test_sync_client_whoami(sync_client: HorizonClientSync, user: User):
    assert sync_client.whoami() == UserResponseV1(
        id=user.id,
        username=user.username,
    )

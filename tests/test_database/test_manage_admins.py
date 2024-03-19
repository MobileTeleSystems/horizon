# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import select

from horizon.backend.db.models import User
from horizon.backend.scripts.manage_admins import add_admins, remove_admins

pytestmark = [pytest.mark.asyncio]


@pytest.mark.parametrize(
    "usernames",
    [
        (["testadmin1", "testadmin2"]),
    ],
)
async def test_add_admins(async_session, usernames):
    await add_admins(async_session, usernames)

    for username in usernames:
        result = await async_session.execute(select(User).filter_by(username=username))
        user = result.scalars().first()
        assert user is not None
        assert user.is_admin == True


@pytest.mark.parametrize(
    "usernames",
    [
        (["testadmin1", "testadmin2"]),
    ],
)
async def test_remove_admins(async_session, usernames):
    await add_admins(async_session, usernames)

    await remove_admins(async_session, usernames)

    for username in usernames:
        result = await async_session.execute(select(User).filter_by(username=username))
        user = result.scalars().first()
        assert user is not None
        assert user.is_admin == False

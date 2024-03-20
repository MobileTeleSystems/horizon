# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.backend.db.models import User
from horizon.backend.scripts.manage_admins import add_admins, remove_admins

pytestmark = [pytest.mark.asyncio]


async def cleanup_users(async_session: AsyncSession, usernames: list):
    for username in usernames:
        await async_session.execute(delete(User).where(User.username == username))
    await async_session.commit()


@pytest.mark.parametrize(
    "additional_usernames",
    [
        (["testadmin1", "testadmin2"]),
    ],
)
async def test_add_admins(async_session: AsyncSession, user: User, additional_usernames: list):
    usernames = [user.username] + additional_usernames

    await add_admins(async_session, usernames)

    for username in usernames:
        result = await async_session.execute(select(User).filter_by(username=username))
        user = result.scalars().first()
        assert user is not None
        assert user.is_admin

    await cleanup_users(async_session, additional_usernames)


@pytest.mark.parametrize(
    "additional_usernames",
    [
        (["testadmin1", "testadmin2"]),
    ],
)
async def test_remove_admins_with_existing_user(async_session: AsyncSession, user: User, additional_usernames: list):
    usernames = [user.username] + additional_usernames

    await add_admins(async_session, usernames)

    await remove_admins(async_session, usernames)

    for username in usernames:
        result = await async_session.execute(select(User).filter_by(username=username))
        user = result.scalars().first()
        assert user is not None
        assert not user.is_admin

    await cleanup_users(async_session, additional_usernames)

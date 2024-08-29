# SPDX-FileCopyrightText: 2023 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import logging

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.backend.db.models import User
from horizon.backend.scripts.manage_admins import add_admins, list_admins, remove_admins

pytestmark = [pytest.mark.asyncio]


@pytest.mark.parametrize("users", [(10, {})], indirect=True)
async def test_add_admins(caplog, async_session: AsyncSession, new_user: User, users: list[User]):
    expected_admins = [user.username for user in users[:5]] + [new_user.username]
    expected_not_admins = [user.username for user in users[5:]]

    with caplog.at_level(logging.INFO):
        await add_admins(async_session, expected_admins)

    for username in expected_admins:
        assert repr(username) in caplog.text

    for username in expected_not_admins:
        assert repr(username) not in caplog.text

    admins_query = select(User).where(User.username.in_(expected_admins))
    admins_query_result = await async_session.execute(admins_query)
    admins = admins_query_result.scalars().all()

    assert set(expected_admins) == {user.username for user in admins}
    for admin in admins:
        assert admin.is_admin

    not_admins_query = select(User).where(User.username.in_(expected_not_admins))
    not_admins_query_result = await async_session.execute(not_admins_query)
    not_admins = not_admins_query_result.scalars().all()

    assert set(expected_not_admins) == {user.username for user in not_admins}
    for user in not_admins:
        assert not user.is_admin


@pytest.mark.parametrize("users", [(10, {})], indirect=True)
async def test_remove_admins(caplog, async_session: AsyncSession, new_user: User, users: list[User]):
    # users 0 and 1 are admins, 2-10 are not. missing username is ignored
    to_create = [user.username for user in users[:5]]
    to_delete = [user.username for user in users[2:]] + [new_user.username]

    expected_admins = [user.username for user in users[:2]]
    expected_not_admins = [user.username for user in users[2:]]

    await add_admins(async_session, to_create)

    caplog.clear()
    with caplog.at_level(logging.INFO):
        await remove_admins(async_session, to_delete)

    for username in expected_admins:
        assert repr(username) not in caplog.text

    for username in expected_not_admins:
        assert repr(username) in caplog.text

    admins_query = select(User).where(User.username.in_(expected_admins))
    admins_query_result = await async_session.execute(admins_query)
    admins = admins_query_result.scalars().all()

    assert set(expected_admins) == {user.username for user in admins}
    for admin in admins:
        assert admin.is_admin

    not_admins_query = select(User).where(User.username.in_(expected_not_admins))
    not_admins_query_result = await async_session.execute(not_admins_query)
    not_admins = not_admins_query_result.scalars().all()

    assert set(expected_not_admins) == {user.username for user in not_admins}
    for user in not_admins:
        assert not user.is_admin


@pytest.mark.parametrize("users", [(10, {})], indirect=True)
async def test_list_admins(caplog, async_session: AsyncSession, users: list[User]):
    expected_admins = [user.username for user in users[:5]]
    expected_not_admins = [user.username for user in users[5:]]

    await add_admins(async_session, expected_admins)

    caplog.clear()
    with caplog.at_level(logging.INFO):
        await list_admins(async_session)

    for username in expected_admins:
        assert repr(username) in caplog.text

    for username in expected_not_admins:
        assert repr(username) not in caplog.text

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import AsyncContextManager, Callable

import pytest
import pytest_asyncio
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.backend.db.models import (
    Namespace,
    NamespaceUser,
    NamespaceUserRoleInt,
    User,
)


@pytest_asyncio.fixture
async def namespace_with_users(
    request: pytest.FixtureRequest,
    namespace: Namespace,
    async_session_factory: Callable[[], AsyncContextManager[AsyncSession]],
) -> AsyncGenerator[None, None]:
    users_roles = request.param

    async with async_session_factory() as async_session:
        created_users = []
        original_owner_id = namespace.owner_id
        for username, role in users_roles:
            user = User(username=username, is_active=True)
            async_session.add(user)
            await async_session.commit()
            created_users.append(user)

            if role != NamespaceUserRoleInt.GUEST:
                if role == NamespaceUserRoleInt.OWNER:
                    namespace.owner_id = user.id
                else:
                    namespace_user = NamespaceUser(namespace_id=namespace.id, user_id=user.id, role=role.name)
                    async_session.add(namespace_user)

                await async_session.commit()

    yield

    async with async_session_factory() as async_session:
        for user in created_users:
            owned_namespaces = await async_session.execute(select(Namespace).where(Namespace.owner_id == user.id))
            for owned_namespace in owned_namespaces.scalars().all():
                owned_namespace.owner_id = original_owner_id
                async_session.add(owned_namespace)

            await async_session.execute(delete(NamespaceUser).where(NamespaceUser.user_id == user.id))
            await async_session.execute(delete(User).where(User.id == user.id))

        await async_session.commit()

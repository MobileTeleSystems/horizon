# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from horizon.db.repositories.hwm import HWMRepository
from horizon.db.repositories.hwm_history import HWMHistoryRepository
from horizon.db.repositories.namespace import NamespaceRepository
from horizon.db.repositories.user import UserRepository
from horizon.dependencies.stub import Stub


class UnitOfWork:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(Stub(AsyncSession))],
    ):
        self._session = session
        self.namespace = NamespaceRepository(session=session)
        self.hwm_history = HWMHistoryRepository(session=session)
        self.user = UserRepository(session=session)
        self.hwm = HWMRepository(session=session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()

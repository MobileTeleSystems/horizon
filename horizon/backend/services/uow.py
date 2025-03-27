# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from horizon.backend.db.repositories import (
    CredentialsCacheRepository,
    HWMHistoryRepository,
    HWMRepository,
    NamespaceHistoryRepository,
    NamespaceRepository,
    UserRepository,
)
from horizon.backend.dependencies import Stub


class UnitOfWork:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(Stub(AsyncSession))],
    ):
        self._session = session
        self.namespace = NamespaceRepository(session=session)
        self.hwm_history = HWMHistoryRepository(session=session)
        self.namespace_history = NamespaceHistoryRepository(session=session)
        self.user = UserRepository(session=session)
        self.hwm = HWMRepository(session=session)
        self.credentials_cache = CredentialsCacheRepository(session=session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self._session.rollback()
        else:
            await self._session.commit()

# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from typing import Optional

from horizon.backend.db.models import CredentialsCache
from horizon.backend.db.repositories.base import Repository


class CredentialsCacheRepository(Repository[CredentialsCache]):
    async def get_by_login(self, login: str) -> Optional[CredentialsCache]:
        return await self._get(CredentialsCache.login == login)

    async def create_or_update(
        self,
        login: str,
        data: dict,
    ) -> CredentialsCache:
        result = await self._update([CredentialsCache.login == login], changes=data)
        if not result:
            result = await self._create(data={"login": login, **data})

        await self._session.flush()
        return result

    async def delete(self, _id: int) -> None:
        await self._delete(_id)
        await self._session.flush()

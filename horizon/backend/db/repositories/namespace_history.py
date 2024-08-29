# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from horizon.backend.db.models import NamespaceHistory
from horizon.backend.db.repositories.base import Repository
from horizon.commons.dto import Pagination


class NamespaceHistoryRepository(Repository[NamespaceHistory]):
    async def paginate(
        self,
        namespace_id: int,
        page: int,
        page_size: int,
    ) -> Pagination[NamespaceHistory]:
        return await self._paginate(
            where=[
                NamespaceHistory.namespace_id == namespace_id,
            ],
            order_by=[NamespaceHistory.changed_at.desc()],
            page=page,
            page_size=page_size,
        )

    async def create(self, namespace_id: int, data: dict) -> NamespaceHistory:
        action = data.get("action", "Created")

        result = await self._create(
            data={
                **data,
                "namespace_id": namespace_id,
                "action": action,
            },
        )
        await self._session.flush()
        return result

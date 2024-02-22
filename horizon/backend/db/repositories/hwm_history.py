# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from horizon.backend.db.models import HWMHistory
from horizon.backend.db.repositories.base import Repository
from horizon.commons.dto import Pagination


class HWMHistoryRepository(Repository[HWMHistory]):
    async def paginate(
        self,
        hwm_id: int,
        page: int,
        page_size: int,
    ) -> Pagination[HWMHistory]:
        return await self._paginate(
            where=[
                HWMHistory.hwm_id == hwm_id,
            ],
            order_by=[HWMHistory.changed_at.desc()],
            page=page,
            page_size=page_size,
        )

    async def create(self, hwm_id: int, data: dict) -> HWMHistory:
        action = data.get("action", "Created")

        result = await self._create(
            data={
                **data,
                "hwm_id": hwm_id,
                "action": action,
            },
        )
        await self._session.flush()
        return result

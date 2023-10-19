# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from app.db.models import HWMHistory
from app.db.repositories.base import Repository
from app.dto.pagination import Pagination


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
                HWMHistory.is_deleted.is_(False),
            ],
            order_by=[HWMHistory.changed_at.desc()],
            page=page,
            page_size=page_size,
        )

    async def create(self, hwm_id: int, data: dict) -> HWMHistory:
        result = await self._create(
            data={
                **data,
                "hwm_id": hwm_id,
            },
        )
        await self._session.flush()
        return result

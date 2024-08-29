# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
from typing import List, Sequence

from sqlalchemy import SQLColumnExpression, delete, select
from sqlalchemy.exc import IntegrityError

from horizon.backend.db.models import HWM, HWMHistory, User
from horizon.backend.db.repositories.base import Repository
from horizon.commons.dto.pagination import Pagination
from horizon.commons.exceptions.entity import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


class HWMRepository(Repository[HWM]):
    async def paginate(
        self,
        namespace_id: int,
        page: int,
        page_size: int,
        name: str | None = None,
    ) -> Pagination[HWM]:
        where: list[SQLColumnExpression] = [
            HWM.namespace_id == namespace_id,
        ]
        if name:
            where.append(HWM.name == name)

        return await self._paginate(
            where=where,
            order_by=[HWM.name],
            page=page,
            page_size=page_size,
        )

    async def count(self) -> int:
        return await self._count()

    async def get(
        self,
        hwm_id: int,
    ) -> HWM:
        result = await self._get(
            HWM.id == hwm_id,
        )
        if not result:
            raise EntityNotFoundError("HWM", "id", hwm_id)
        return result

    async def create(
        self,
        data: dict,
        user: User,
    ) -> HWM:
        try:
            result = await self._create(data={**data, "changed_by_user_id": user.id})
            await self._session.flush()
            return result
        except IntegrityError as e:
            constraint = e.__cause__.__cause__.constraint_name  # type: ignore[union-attr]

            if constraint == "fk__hwm__namespace_id__namespace":
                raise EntityNotFoundError("Namespace", "id", data["namespace_id"]) from e

            if constraint == "hwm_name_unique_per_namespace":
                raise EntityAlreadyExistsError("HWM", "name", data["name"]) from e

            raise

    async def update(
        self,
        hwm_id: int,
        changes: dict,
        user: User,
    ) -> HWM:
        try:
            result = await self._update(
                where=[HWM.id == hwm_id],
                changes={**changes, "changed_by_user_id": user.id},
            )
            if result is None:
                raise EntityNotFoundError("HWM", "id", hwm_id)

            await self._session.flush()
            await self._session.refresh(result)
            return result
        except IntegrityError as e:
            raise EntityAlreadyExistsError("HWM", "name", changes["name"]) from e

    async def delete(
        self,
        hwm_id: int,
    ) -> HWM:
        hwm = await self.get(hwm_id)
        await self._session.delete(hwm)
        await self._session.flush()
        return hwm

    async def bulk_delete(self, namespace_id: int, hwm_ids: List[int]) -> Sequence[HWM]:
        result = await self._session.execute(select(HWM).where(HWM.id.in_(hwm_ids), HWM.namespace_id == namespace_id))
        hwms_to_delete = result.scalars().all()

        if hwms_to_delete:
            await self._session.execute(delete(HWM).where(HWM.id.in_([hwm.id for hwm in hwms_to_delete])))

        return hwms_to_delete

    async def bulk_copy(
        self,
        source_namespace_id: int,
        target_namespace_id: int,
        hwm_ids: list[int],
        with_history: bool,
    ) -> Sequence[HWM]:
        result = await self._session.execute(
            select(HWM).where(HWM.id.in_(hwm_ids), HWM.namespace_id == source_namespace_id),
        )
        hwms = result.scalars().all()
        copied_hwms = []

        for hwm in hwms:
            new_hwm = HWM(
                **hwm.to_dict(exclude={"id", "namespace_id"}),
                namespace_id=target_namespace_id,
            )
            self._session.add(new_hwm)
            copied_hwms.append(new_hwm)

        try:
            await self._session.flush()
        except IntegrityError as e:
            constraint = e.__cause__.__cause__.constraint_name  # type: ignore[union-attr]
            if constraint == "hwm_name_unique_per_namespace":
                hwm_name = re.search(r"Key \(namespace_id, name\)=\(\d+, (.+)\) already exists.", e.__cause__.__cause__.detail).group(1)  # type: ignore[union-attr]
                raise EntityAlreadyExistsError("HWM", "name", hwm_name) from e

        if with_history:
            for original_hwm, copied_hwm in zip(hwms, copied_hwms):
                history = await self._session.execute(
                    select(HWMHistory).where(HWMHistory.hwm_id == original_hwm.id),
                )
                history = history.scalars().all()  # type: ignore
                for record in history:
                    new_history_record = HWMHistory(
                        **record.to_dict(exclude={"id", "hwm_id"}),
                        hwm_id=copied_hwm.id,
                    )
                    self._session.add(new_history_record)

            await self._session.flush()

        return copied_hwms

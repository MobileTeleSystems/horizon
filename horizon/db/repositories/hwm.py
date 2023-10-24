# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from sqlalchemy.exc import IntegrityError

from horizon.db.models import HWM
from horizon.db.models.user import User
from horizon.db.repositories.base import Repository
from horizon_commons.dto.pagination import Pagination
from horizon_commons.dto.unset import Unset
from horizon_commons.exceptions.entity import (
    EntityAlreadyExistsError,
    EntityInvalidError,
    EntityNotFoundError,
)


class HWMRepository(Repository[HWM]):
    async def paginate(
        self,
        namespace_id: int,
        page: int,
        page_size: int,
    ) -> Pagination[HWM]:
        return await self._paginate(
            where=[HWM.namespace_id == namespace_id, HWM.is_deleted.is_(False)],
            order_by=[HWM.name],
            page=page,
            page_size=page_size,
        )

    async def get_by_name(
        self,
        namespace_id: int,
        name: str,
    ) -> HWM:
        result = await self._get(
            HWM.namespace_id == namespace_id,
            HWM.name == name,
            HWM.is_deleted.is_(False),
        )
        if result is None:
            raise EntityNotFoundError(HWM, "name", name)
        return result

    async def write(
        self,
        namespace_id: int,
        name: str,
        data: dict,
        user: User,
    ) -> HWM:
        try:
            result = await self._update(
                where=[HWM.namespace_id == namespace_id, HWM.name == name, HWM.is_deleted.is_(False)],
                changes={**data, "changed_by_user_id": user.id},
            )
            if result is None:
                if "type" not in data:
                    raise EntityInvalidError(HWM, "type", Unset())
                if "value" not in data:
                    raise EntityInvalidError(HWM, "value", Unset())

                result = await self._create(
                    data={
                        **data,
                        "namespace_id": namespace_id,
                        "name": name,
                        "changed_by_user_id": user.id,
                    },
                )
            await self._session.flush()
            return result
        except IntegrityError as e:
            raise EntityAlreadyExistsError(HWM, "name", name) from e

    async def delete(
        self,
        namespace_id: int,
        name: str,
        user: User,
    ) -> HWM:
        result = await self._update(
            where=[HWM.namespace_id == namespace_id, HWM.name == name, HWM.is_deleted.is_(False)],
            changes={"is_deleted": True, "changed_by_user_id": user.id},
        )
        if result is None:
            raise EntityNotFoundError(HWM, "name", name)

        await self._session.flush()
        return result

# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends, status
from typing_extensions import Annotated

from horizon.backend.db.models import NamespaceUserRole, User
from horizon.backend.services import UnitOfWork, current_user
from horizon.commons.errors import get_error_responses
from horizon.commons.schemas.v1 import (
    HWMCreateRequestV1,
    HWMPaginateQueryV1,
    HWMResponseV1,
    HWMUpdateRequestV1,
    PageResponseV1,
)

router = APIRouter(prefix="/hwm", tags=["HWM"], responses=get_error_responses())


@router.get(
    "/",
    summary="Paginate HWM",
    dependencies=[Depends(current_user)],
)
async def paginate_hwm(
    pagination_args: Annotated[HWMPaginateQueryV1, Depends()],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> PageResponseV1[HWMResponseV1]:
    pagination = await unit_of_work.hwm.paginate(**pagination_args.dict())
    return PageResponseV1[HWMResponseV1].from_pagination(pagination)


@router.get(
    "/{hwm_id}",
    summary="Get HWM",
    dependencies=[Depends(current_user)],
)
async def get_hwm(
    hwm_id: int,
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> HWMResponseV1:
    hwm = await unit_of_work.hwm.get(hwm_id)
    return HWMResponseV1.from_orm(hwm)


@router.post(
    "/",
    summary="Create HWM",
    status_code=status.HTTP_201_CREATED,
)
async def create_hwm(
    data: HWMCreateRequestV1,
    user: Annotated[User, Depends(current_user)],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> HWMResponseV1:
    async with unit_of_work:
        await unit_of_work.namespace.check_user_permission(
            user=user,
            required_role=NamespaceUserRole.DEVELOPER,
            namespace_id=data.namespace_id,
        )
        hwm = await unit_of_work.hwm.create(
            data=data.dict(exclude_unset=True),
            user=user,
        )
        await unit_of_work.hwm_history.create(
            hwm_id=hwm.id,
            data=hwm.to_dict(exclude={"id"}),
        )
    return HWMResponseV1.from_orm(hwm)


@router.patch(
    "/{hwm_id}",
    summary="Update HWM",
)
async def update_hwm(
    hwm_id: int,
    changes: HWMUpdateRequestV1,
    user: Annotated[User, Depends(current_user)],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> HWMResponseV1:
    async with unit_of_work:
        hwm = await unit_of_work.hwm.get(hwm_id)
        await unit_of_work.namespace.check_user_permission(
            user=user,
            required_role=NamespaceUserRole.DEVELOPER,
            namespace_id=hwm.namespace_id,
        )
        hwm = await unit_of_work.hwm.update(
            hwm_id=hwm_id,
            changes=changes.dict(exclude_unset=True),
            user=user,
        )
        await unit_of_work.hwm_history.create(
            hwm_id=hwm.id,
            data={
                **hwm.to_dict(exclude={"id"}),
                "action": "Updated",
            },
        )
    return HWMResponseV1.from_orm(hwm)


@router.delete(
    "/{hwm_id}",
    summary="Delete HWM",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_hwm(
    hwm_id: int,
    user: Annotated[User, Depends(current_user)],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> None:
    async with unit_of_work:
        hwm = await unit_of_work.hwm.get(hwm_id)
        await unit_of_work.namespace.check_user_permission(
            user=user,
            required_role=NamespaceUserRole.MAINTAINER,
            namespace_id=hwm.namespace_id,
        )
        hwm = await unit_of_work.hwm.delete(hwm_id=hwm_id, user=user)
        await unit_of_work.hwm_history.create(
            hwm_id=hwm.id,
            data={**hwm.to_dict(exclude={"id"}), "action": "Deleted"},
        )

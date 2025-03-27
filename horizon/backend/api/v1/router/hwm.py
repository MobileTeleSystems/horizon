# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0


from typing import Annotated

from fastapi import APIRouter, Depends, status

from horizon.backend.db.models import NamespaceUserRoleInt, User
from horizon.backend.services import UnitOfWork, current_user
from horizon.commons.errors import get_error_responses
from horizon.commons.schemas.v1 import (
    HWMBulkCopyRequestV1,
    HWMBulkDeleteRequestV1,
    HWMCreateRequestV1,
    HWMListResponseV1,
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
            user_id=user.id,
            required_role=NamespaceUserRoleInt.DEVELOPER,
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
            user_id=user.id,
            required_role=NamespaceUserRoleInt.DEVELOPER,
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
            user_id=user.id,
            required_role=NamespaceUserRoleInt.MAINTAINER,
            namespace_id=hwm.namespace_id,
        )
        hwm = await unit_of_work.hwm.delete(hwm_id=hwm_id)
        await unit_of_work.hwm_history.create(
            hwm_id=hwm.id,
            data={**hwm.to_dict(exclude={"id"}), "changed_by_user_id": user.id, "action": "Deleted"},
        )


@router.delete(
    "/",
    summary="Bulk Delete HWM",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def bulk_delete_hwm(
    changes: HWMBulkDeleteRequestV1,
    user: Annotated[User, Depends(current_user)],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> None:
    async with unit_of_work:
        await unit_of_work.namespace.check_user_permission(
            user_id=user.id,
            required_role=NamespaceUserRoleInt.MAINTAINER,
            namespace_id=changes.namespace_id,
        )
        deleted_hwms = await unit_of_work.hwm.bulk_delete(namespace_id=changes.namespace_id, hwm_ids=changes.hwm_ids)

        hwm_history_data = [
            {"hwm_id": hwm.id, "changed_by_user_id": user.id, "action": "Deleted", **hwm.to_dict(exclude={"id"})}
            for hwm in deleted_hwms
        ]

        await unit_of_work.hwm_history.bulk_create(hwm_data=hwm_history_data)


@router.post(
    "/copy",
    summary="Copy HWMs to another namespace",
    status_code=status.HTTP_201_CREATED,
)
async def copy_hwms(
    copy_request: HWMBulkCopyRequestV1,
    user: Annotated[User, Depends(current_user)],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> HWMListResponseV1:
    async with unit_of_work:
        await unit_of_work.namespace.check_user_permission(
            user_id=user.id,
            namespace_id=copy_request.target_namespace_id,
            required_role=NamespaceUserRoleInt.DEVELOPER,
        )

        source_namespace = await unit_of_work.namespace.get(copy_request.source_namespace_id)
        copied_hwms = await unit_of_work.hwm.bulk_copy(
            source_namespace_id=source_namespace.id,
            target_namespace_id=copy_request.target_namespace_id,
            hwm_ids=copy_request.hwm_ids,
            with_history=copy_request.with_history,
        )

        hwm_history_data = []
        for copied_hwm in copied_hwms:
            history_record = {
                **copied_hwm.to_dict(exclude={"id", "changed_by_user_id"}),
                "hwm_id": copied_hwm.id,
                "action": f"Copied from namespace {copy_request.source_namespace_id} "
                f"to namespace {copy_request.target_namespace_id}",
                "changed_by_user_id": user.id,
            }
            hwm_history_data.append(history_record)

        await unit_of_work.hwm_history.bulk_create(hwm_history_data)
        return HWMListResponseV1(hwms=[HWMResponseV1.from_orm(hwm) for hwm in copied_hwms])

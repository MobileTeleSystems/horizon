# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Annotated

from fastapi import APIRouter, Depends, status

from horizon.db.models.user import User
from horizon.services import UnitOfWork, current_user
from horizon_commons.errors import get_error_responses
from horizon_commons.schemas.v1 import (
    HWMHistoryResponseV1,
    HWMPaginateQueryV1,
    HWMResponseV1,
    HWMWriteRequestV1,
    NamespaceCreateRequestV1,
    NamespacePaginateQueryV1,
    NamespaceResponseV1,
    NamespaceUpdateRequestV1,
    PageResponseV1,
    PaginateQueryV1,
)

router = APIRouter(prefix="/namespaces", tags=["Namespace"], responses=get_error_responses())


@router.get(
    "/",
    description="Paginage namespaces",
    dependencies=[Depends(current_user)],
)
async def paginate_namespaces(
    pagination_args: Annotated[NamespacePaginateQueryV1, Depends()],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> PageResponseV1[NamespaceResponseV1]:
    pagination = await unit_of_work.namespace.paginate(**pagination_args.dict())
    return PageResponseV1[NamespaceResponseV1].from_pagination(pagination)


@router.post(
    "/",
    description="Create namespace",
    status_code=status.HTTP_201_CREATED,
)
async def create_namespace(
    data: NamespaceCreateRequestV1,
    unit_of_work: Annotated[UnitOfWork, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> NamespaceResponseV1:
    async with unit_of_work:
        namespace = await unit_of_work.namespace.create(**data.dict(), user=user)
    return NamespaceResponseV1.from_orm(namespace)


@router.get(
    "/{namespace_name}",
    description="Get namespace by name",
    dependencies=[Depends(current_user)],
)
async def get_namespace(
    namespace_name: str,
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> NamespaceResponseV1:
    namespace = await unit_of_work.namespace.get_by_name(namespace_name)
    return NamespaceResponseV1.from_orm(namespace)


@router.patch(
    "/{namespace_name}",
    description="Update namespace",
)
async def update_namespace(
    namespace_name: str,
    changes: NamespaceUpdateRequestV1,
    unit_of_work: Annotated[UnitOfWork, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> NamespaceResponseV1:
    async with unit_of_work:
        namespace = await unit_of_work.namespace.update(
            name=namespace_name,
            changes=changes.dict(exclude_defaults=True),
            user=user,
        )
    return NamespaceResponseV1.from_orm(namespace)


@router.delete(
    "/{namespace_name}",
    description="Delete namespace",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_namespace(
    namespace_name: str,
    user: Annotated[User, Depends(current_user)],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> None:
    async with unit_of_work:
        await unit_of_work.namespace.delete(
            name=namespace_name,
            user=user,
        )


@router.get(
    "/{namespace_name}/hwm/",
    description="Paginate HWM",
    dependencies=[Depends(current_user)],
)
async def paginate_hwm(
    namespace_name: str,
    pagination_args: Annotated[HWMPaginateQueryV1, Depends()],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> PageResponseV1[HWMResponseV1]:
    namespace = await unit_of_work.namespace.get_by_name(namespace_name)
    pagination = await unit_of_work.hwm.paginate(
        namespace_id=namespace.id,
        **pagination_args.dict(),
    )
    return PageResponseV1[HWMResponseV1].from_pagination(pagination)


@router.get(
    "/{namespace_name}/hwm/{hwm_name}",
    description="Get HWM by name",
    dependencies=[Depends(current_user)],
)
async def get_hwm(
    namespace_name: str,
    hwm_name: str,
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> HWMResponseV1:
    namespace = await unit_of_work.namespace.get_by_name(namespace_name)
    hwm = await unit_of_work.hwm.get_by_name(
        namespace_id=namespace.id,
        name=hwm_name,
    )
    return HWMResponseV1.from_orm(hwm)


@router.patch(
    "/{namespace_name}/hwm/{hwm_name}",
    description="Write HWM value",
)
async def write_hwm(
    namespace_name: str,
    hwm_name: str,
    data: HWMWriteRequestV1,
    user: Annotated[User, Depends(current_user)],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> HWMResponseV1:
    namespace = await unit_of_work.namespace.get_by_name(namespace_name)
    async with unit_of_work:
        hwm = await unit_of_work.hwm.write(
            namespace_id=namespace.id,
            name=hwm_name,
            data=data.dict(exclude_unset=True),
            user=user,
        )
        await unit_of_work.hwm_history.create(
            hwm_id=hwm.id,
            data=hwm.to_dict(exclude={"id"}),
        )
    return HWMResponseV1.from_orm(hwm)


@router.delete(
    "/{namespace_name}/hwm/{hwm_name}",
    description="Delete HWM",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_hwm(
    namespace_name: str,
    hwm_name: str,
    user: Annotated[User, Depends(current_user)],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> None:
    namespace = await unit_of_work.namespace.get_by_name(namespace_name)
    async with unit_of_work:
        hwm = await unit_of_work.hwm.delete(
            namespace_id=namespace.id,
            name=hwm_name,
            user=user,
        )
        await unit_of_work.hwm_history.create(
            hwm_id=hwm.id,
            data=hwm.to_dict(exclude={"id"}),
        )


@router.get(
    "/{namespace_name}/hwm/{hwm_name}/history",
    description="Paginate HWM history",
    dependencies=[Depends(current_user)],
)
async def paginate_hwm_history(
    namespace_name: str,
    hwm_name: str,
    pagination_args: Annotated[PaginateQueryV1, Depends()],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> PageResponseV1[HWMHistoryResponseV1]:
    namespace = await unit_of_work.namespace.get_by_name(namespace_name)
    hwm = await unit_of_work.hwm.get_by_name(
        namespace_id=namespace.id,
        name=hwm_name,
    )
    pagination = await unit_of_work.hwm_history.paginate(
        hwm_id=hwm.id,
        page=pagination_args.page,
        page_size=pagination_args.page_size,
    )
    return PageResponseV1[HWMHistoryResponseV1].from_pagination(pagination)

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Annotated

from fastapi import APIRouter, Depends, status

from horizon.db.models.user import User
from horizon.db.repositories.hwm import HWMRepository
from horizon.db.repositories.hwm_history import HWMHistoryRepository
from horizon.db.repositories.namespace import NamespaceRepository
from horizon.dependencies import current_user
from horizon_commons.errors import get_error_responses
from horizon_commons.schemas.v1 import (
    CreateNamespaceRequestV1,
    NamespaceResponseV1,
    PageResponseV1,
    PaginateNamespaceQueryV1,
    PaginateQueryV1,
    ReadHWMHistorySchemaV1,
    ReadHWMSchemaV1,
    UpdateNamespaceRequestV1,
    WriteHWMSchemaV1,
)

router = APIRouter(prefix="/namespaces", tags=["Namespace"], responses=get_error_responses())


@router.get(
    "/",
    description="Paginage namespaces",
)
async def paginate_namespaces(
    pagination_args: Annotated[PaginateNamespaceQueryV1, Depends()],
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    _user: Annotated[User, Depends(current_user)],
) -> PageResponseV1[NamespaceResponseV1]:
    pagination = await namespace_repo.paginate(**pagination_args.dict())
    return PageResponseV1[NamespaceResponseV1].from_pagination(pagination)


@router.post(
    "/",
    description="Create namespace",
    status_code=status.HTTP_201_CREATED,
)
async def create_namespace(
    data: CreateNamespaceRequestV1,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> NamespaceResponseV1:
    namespace = await namespace_repo.create(**data.dict(), user=user)
    return NamespaceResponseV1.from_orm(namespace)


@router.get(
    "/{namespace_name}",
    description="Get namespace by name",
)
async def get_namespace(
    namespace_name: str,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    _user: Annotated[User, Depends(current_user)],
) -> NamespaceResponseV1:
    namespace = await namespace_repo.get_by_name(namespace_name)
    return NamespaceResponseV1.from_orm(namespace)


@router.patch(
    "/{namespace_name}",
    description="Update namespace",
)
async def update_namespace(
    namespace_name: str,
    changes: UpdateNamespaceRequestV1,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> NamespaceResponseV1:
    namespace = await namespace_repo.update(
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
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> None:
    await namespace_repo.delete(
        name=namespace_name,
        user=user,
    )


@router.get(
    "/{namespace_name}/hwm/",
    description="Paginate HWM",
)
async def paginate_hwm(
    namespace_name: str,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    pagination_args: Annotated[PaginateQueryV1, Depends()],
    hwm_repo: Annotated[HWMRepository, Depends()],
    _user: Annotated[User, Depends(current_user)],
) -> PageResponseV1[ReadHWMSchemaV1]:
    namespace = await namespace_repo.get_by_name(namespace_name)
    pagination = await hwm_repo.paginate(
        namespace_id=namespace.id,
        page=pagination_args.page,
        page_size=pagination_args.page_size,
    )
    return PageResponseV1[ReadHWMSchemaV1].from_pagination(pagination)


@router.get(
    "/{namespace_name}/hwm/{hwm_name}",
    description="Get HWM by name",
)
async def get_hwm(
    namespace_name: str,
    hwm_name: str,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    hwm_repo: Annotated[HWMRepository, Depends()],
    _user: Annotated[User, Depends(current_user)],
) -> ReadHWMSchemaV1:
    namespace = await namespace_repo.get_by_name(namespace_name)
    hwm = await hwm_repo.get_by_name(
        namespace_id=namespace.id,
        name=hwm_name,
    )
    return ReadHWMSchemaV1.from_orm(hwm)


@router.patch(
    "/{namespace_name}/hwm/{hwm_name}",
    description="Write HWM value",
)
async def write_hwm(
    namespace_name: str,
    hwm_name: str,
    data: WriteHWMSchemaV1,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    hwm_repo: Annotated[HWMRepository, Depends()],
    hwm_history_repo: Annotated[HWMHistoryRepository, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> ReadHWMSchemaV1:
    namespace = await namespace_repo.get_by_name(namespace_name)
    hwm = await hwm_repo.write(
        namespace_id=namespace.id,
        name=hwm_name,
        data=data.dict(exclude_unset=True),
        user=user,
    )
    await hwm_history_repo.create(
        hwm_id=hwm.id,
        data=hwm.to_dict(exclude={"id"}),
    )
    return ReadHWMSchemaV1.from_orm(hwm)


@router.delete(
    "/{namespace_name}/hwm/{hwm_name}",
    description="Delete HWM",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_hwm(
    namespace_name: str,
    hwm_name: str,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    hwm_repo: Annotated[HWMRepository, Depends()],
    hwm_history_repo: Annotated[HWMHistoryRepository, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> None:
    namespace = await namespace_repo.get_by_name(namespace_name)
    hwm = await hwm_repo.delete(
        namespace_id=namespace.id,
        name=hwm_name,
        user=user,
    )
    await hwm_history_repo.create(
        hwm_id=hwm.id,
        data=hwm.to_dict(exclude={"id"}),
    )


@router.get(
    "/{namespace_name}/hwm/{hwm_name}/history",
    description="Paginate HWM history",
)
async def paginate_hwm_history(
    namespace_name: str,
    hwm_name: str,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    pagination_args: Annotated[PaginateQueryV1, Depends()],
    hwm_repo: Annotated[HWMRepository, Depends()],
    hwm_history_repo: Annotated[HWMHistoryRepository, Depends()],
    _user: Annotated[User, Depends(current_user)],
) -> PageResponseV1[ReadHWMHistorySchemaV1]:
    namespace = await namespace_repo.get_by_name(namespace_name)
    hwm = await hwm_repo.get_by_name(
        namespace_id=namespace.id,
        name=hwm_name,
    )
    pagination = await hwm_history_repo.paginate(
        hwm_id=hwm.id,
        page=pagination_args.page,
        page_size=pagination_args.page_size,
    )
    return PageResponseV1[ReadHWMHistorySchemaV1].from_pagination(pagination)

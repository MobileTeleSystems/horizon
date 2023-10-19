# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.errors import get_error_responses
from app.api.pagination.query import PaginationArgs
from app.api.pagination.schemas import PageSchema
from app.api.v1.namespaces.schemas import (
    CreateNamespaceSchema,
    ReadHWMHistorySchema,
    ReadHWMSchema,
    ReadNamespaceSchema,
    UpdateNamespaceSchema,
    WriteHWMSchema,
)
from app.db.models.user import User
from app.db.repositories.hwm import HWMRepository
from app.db.repositories.hwm_history import HWMHistoryRepository
from app.db.repositories.namespace import NamespaceRepository
from app.dependencies import current_user

router = APIRouter(prefix="/namespaces", tags=["Namespace"], responses=get_error_responses())


@router.get(
    "/",
    description="Paginage namespaces",
)
async def paginate_namespaces(
    pagination_args: Annotated[PaginationArgs, Depends()],
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    _user: Annotated[User, Depends(current_user)],
) -> PageSchema[ReadNamespaceSchema]:
    pagination = await namespace_repo.paginate(
        page=pagination_args.page,
        page_size=pagination_args.page_size,
    )
    return PageSchema[ReadNamespaceSchema].from_pagination(pagination)


@router.post(
    "/",
    description="Create namespace",
    status_code=status.HTTP_201_CREATED,
)
async def create_namespace(
    data: CreateNamespaceSchema,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> ReadNamespaceSchema:
    namespace = await namespace_repo.create(**data.dict(), user=user)
    return ReadNamespaceSchema.from_orm(namespace)


@router.get(
    "/{name}",
    description="Get namespace by name",
)
async def get_namespace(
    name: str,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    _user: Annotated[User, Depends(current_user)],
) -> ReadNamespaceSchema:
    namespace = await namespace_repo.get_by_name(name)
    return ReadNamespaceSchema.from_orm(namespace)


@router.patch(
    "/{name}",
    description="Update namespace",
)
async def update_namespace(
    name: str,
    changes: UpdateNamespaceSchema,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> ReadNamespaceSchema:
    namespace = await namespace_repo.update(
        name=name,
        changes=changes.dict(exclude_defaults=True),
        user=user,
    )
    return ReadNamespaceSchema.from_orm(namespace)


@router.delete(
    "/{name}",
    description="Delete namespace",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_namespace(
    name: str,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> None:
    await namespace_repo.delete(
        name=name,
        user=user,
    )


@router.get(
    "/{namespace_name}/hwm/",
    description="Paginate HWM",
)
async def paginate_hwm(
    namespace_name: str,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    pagination_args: Annotated[PaginationArgs, Depends()],
    hwm_repo: Annotated[HWMRepository, Depends()],
    _user: Annotated[User, Depends(current_user)],
) -> PageSchema[ReadHWMSchema]:
    namespace = await namespace_repo.get_by_name(namespace_name)
    pagination = await hwm_repo.paginate(
        namespace_id=namespace.id,
        page=pagination_args.page,
        page_size=pagination_args.page_size,
    )
    return PageSchema[ReadHWMSchema].from_pagination(pagination)


@router.get(
    "/{namespace_name}/hwm/{name}",
    description="Get HWM by name",
)
async def get_hwm(
    namespace_name: str,
    name: str,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    hwm_repo: Annotated[HWMRepository, Depends()],
    _user: Annotated[User, Depends(current_user)],
) -> ReadHWMSchema:
    namespace = await namespace_repo.get_by_name(namespace_name)
    hwm = await hwm_repo.get_by_name(
        namespace_id=namespace.id,
        name=name,
    )
    return ReadHWMSchema.from_orm(hwm)


@router.patch(
    "/{namespace_name}/hwm/{name}",
    description="Write HWM value",
)
async def write_hwm(
    namespace_name: str,
    name: str,
    data: WriteHWMSchema,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    hwm_repo: Annotated[HWMRepository, Depends()],
    hwm_history_repo: Annotated[HWMHistoryRepository, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> ReadHWMSchema:
    namespace = await namespace_repo.get_by_name(namespace_name)
    hwm = await hwm_repo.write(
        namespace_id=namespace.id,
        name=name,
        data=data.dict(exclude_unset=True),
        user=user,
    )
    await hwm_history_repo.create(
        hwm_id=hwm.id,
        data=hwm.to_dict(exclude={"id"}),
    )
    return ReadHWMSchema.from_orm(hwm)


@router.delete(
    "/{namespace_name}/hwm/{name}",
    description="Delete HWM",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_hwm(
    namespace_name: str,
    name: str,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    hwm_repo: Annotated[HWMRepository, Depends()],
    hwm_history_repo: Annotated[HWMHistoryRepository, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> None:
    namespace = await namespace_repo.get_by_name(namespace_name)
    hwm = await hwm_repo.delete(
        namespace_id=namespace.id,
        name=name,
        user=user,
    )
    await hwm_history_repo.create(
        hwm_id=hwm.id,
        data=hwm.to_dict(exclude={"id"}),
    )


@router.get(
    "/{namespace_name}/hwm/{name}/history",
    description="Paginate HWM history",
)
async def paginate_hwm_history(
    namespace_name: str,
    name: str,
    namespace_repo: Annotated[NamespaceRepository, Depends()],
    pagination_args: Annotated[PaginationArgs, Depends()],
    hwm_repo: Annotated[HWMRepository, Depends()],
    hwm_history_repo: Annotated[HWMHistoryRepository, Depends()],
    _user: Annotated[User, Depends(current_user)],
) -> PageSchema[ReadHWMHistorySchema]:
    namespace = await namespace_repo.get_by_name(namespace_name)
    hwm = await hwm_repo.get_by_name(
        namespace_id=namespace.id,
        name=name,
    )
    pagination = await hwm_history_repo.paginate(
        hwm_id=hwm.id,
        page=pagination_args.page,
        page_size=pagination_args.page_size,
    )
    return PageSchema[ReadHWMHistorySchema].from_pagination(pagination)

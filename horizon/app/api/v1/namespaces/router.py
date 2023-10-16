# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.errors import get_error_responses
from app.api.pagination.query import PaginationArgs
from app.api.pagination.schemas import PageSchema
from app.api.v1.namespaces.schemas import (
    CreateNamespaceSchema,
    ReadNamespaceSchema,
    UpdateNamespaceSchema,
)
from app.db.models.user import User
from app.db.repositories.namespace import NamespaceRepository
from app.dependencies import current_user

router = APIRouter(prefix="/namespaces", tags=["Namespace"], responses=get_error_responses())


@router.get(
    "/",
    description="Get namespaces list",
)
async def list_namespaces(
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

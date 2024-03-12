# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends
from typing_extensions import Annotated

from horizon.backend.db.models import NamespaceUserRole, User
from horizon.backend.services import UnitOfWork, current_user
from horizon.commons.errors import get_error_responses
from horizon.commons.schemas.v1 import (
    PermissionResponseItemV1,
    PermissionsResponseV1,
    PermissionsUpdateRequestV1,
)

router = APIRouter(prefix="/namespace", tags=["Permissions"], responses=get_error_responses())


@router.get("/{namespace_id}/permissions", summary="Get namespace permissions", dependencies=[Depends(current_user)])
async def get_namespace_permissions(
    namespace_id: int,
    unit_of_work: Annotated[UnitOfWork, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> PermissionsResponseV1:
    async with unit_of_work:
        await unit_of_work.namespace.check_user_permission(
            user_id=user.id,
            namespace_id=namespace_id,
            required_role=NamespaceUserRole.OWNER,
        )
        permissions = await unit_of_work.namespace.get_permissions(namespace_id)
    return PermissionsResponseV1(permissions=[PermissionResponseItemV1(**perm) for perm in permissions])


@router.patch(
    "/{namespace_id}/permissions",
    summary="Update namespace permissions",
    dependencies=[Depends(current_user)],
)
async def update_namespace_permissions(
    namespace_id: int,
    changes: PermissionsUpdateRequestV1,
    unit_of_work: Annotated[UnitOfWork, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> PermissionsResponseV1:
    async with unit_of_work:
        await unit_of_work.namespace.check_user_permission(
            user_id=user.id,
            namespace_id=namespace_id,
            required_role=NamespaceUserRole.OWNER,
        )
        updated_permissions = await unit_of_work.namespace.update_permissions(
            namespace_id=namespace_id,
            owner_id=user.id,
            permissions_update=changes,
        )
    return PermissionsResponseV1(
        permissions=[
            PermissionResponseItemV1(username=perm["username"], role=perm["role"]) for perm in updated_permissions
        ],
    )

# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Set

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
        permissions = await unit_of_work.namespace.get_namespace_users_permissions(namespace_id)
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

        sorted_permissions = sorted(
            changes.permissions,
            key=lambda perm: perm.role == NamespaceUserRole.OWNER.name if perm.role else False,
            reverse=True,
        )

        updated_permissions = []
        seen_user_ids: Set[int] = set()
        owner_changed = {"changed": False}
        for permission in sorted_permissions:
            perm_user = await unit_of_work.user.get_user_by_username(permission.username)

            if permission.role:
                role_enum = NamespaceUserRole[permission.role.upper()]
                await unit_of_work.namespace.update_user_permission(
                    namespace_id,
                    perm_user.id,
                    role_enum,
                    seen_user_ids,
                    owner_changed,
                )
                updated_permissions.append(
                    {"user_id": perm_user.id, "username": permission.username, "role": role_enum.name},
                )
            else:
                await unit_of_work.namespace.delete_permission(namespace_id, perm_user.id)
    return PermissionsResponseV1(
        permissions=[
            PermissionResponseItemV1(username=perm["username"], role=perm["role"]) for perm in updated_permissions
        ],
    )

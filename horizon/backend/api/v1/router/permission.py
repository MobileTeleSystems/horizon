# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends
from typing_extensions import Annotated

from horizon.backend.db.models import NamespaceUserRoleInt, User
from horizon.backend.services import UnitOfWork, current_user
from horizon.commons.errors import get_error_responses
from horizon.commons.exceptions import BadRequestError
from horizon.commons.schemas.v1 import (
    NamespaceUserRole,
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
            required_role=NamespaceUserRoleInt.OWNER,
        )
        permissions_dict = await unit_of_work.namespace.get_namespace_users_permissions(namespace_id)

        permissions_response = [
            PermissionResponseItemV1(username=user.username, role=role.name) for user, role in permissions_dict.items()
        ]

    return PermissionsResponseV1(permissions=permissions_response)


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
            required_role=NamespaceUserRoleInt.OWNER,
        )

        updated_permissions_response = []
        owner_change_detected = False

        for perm in changes.permissions:
            update_user = await unit_of_work.user.get_by_username(perm.username)

            # Ensure the current owner isn't changing their role without assigning a new owner
            if update_user.id == user.id and perm.role != NamespaceUserRole.OWNER:
                if not any(
                    p.role == NamespaceUserRole.OWNER for p in changes.permissions if p.username != user.username
                ):
                    raise BadRequestError(
                        "Operation forbidden: The current owner cannot change their rights without reassigning them to another user.",
                    )

            if perm.role:
                if perm.role == NamespaceUserRole.OWNER and not owner_change_detected:
                    await unit_of_work.namespace.set_new_owner(namespace_id, update_user.id)
                    owner_change_detected = True
                else:
                    role_enum = NamespaceUserRoleInt[perm.role.upper()]
                    await unit_of_work.namespace.update_permission(namespace_id, update_user.id, role_enum)
                updated_permissions_response.append(
                    PermissionResponseItemV1(username=perm.username, role=perm.role),
                )
            else:
                await unit_of_work.namespace.delete_permission(namespace_id, update_user.id)

        return PermissionsResponseV1(permissions=updated_permissions_response)

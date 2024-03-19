# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends
from typing_extensions import Annotated

from horizon.backend.db.models import User
from horizon.backend.services import UnitOfWork, current_user
from horizon.commons.dto import Role
from horizon.commons.errors import get_error_responses
from horizon.commons.exceptions import BadRequestError, PermissionDeniedError
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
    namespace = await unit_of_work.namespace.get(namespace_id)

    role = await unit_of_work.namespace.get_user_role(
        user_id=user.id,
        namespace_id=namespace.id,
    )
    if role != Role.OWNER:
        raise PermissionDeniedError(required_role="OWNER", actual_role=role.name if role else "GUEST")

    roles_dict = await unit_of_work.namespace.get_all_roles(namespace.id)
    permissions_response = [
        PermissionResponseItemV1(username=user.username, role=role) for user, role in roles_dict.items()
    ]

    return PermissionsResponseV1(permissions=permissions_response)


@router.patch(
    "/{namespace_id}/permissions",
    summary="Set namespace permissions",
    dependencies=[Depends(current_user)],
)
async def set_namespace_permissions(  # noqa: WPS231, WPS217
    namespace_id: int,
    changes: PermissionsUpdateRequestV1,
    unit_of_work: Annotated[UnitOfWork, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> PermissionsResponseV1:
    namespace = await unit_of_work.namespace.get(namespace_id)

    role = await unit_of_work.namespace.get_user_role(
        user_id=user.id,
        namespace_id=namespace.id,
    )
    if role != Role.OWNER:
        raise PermissionDeniedError(required_role="OWNER", actual_role=role.name if role else "GUEST")

    async with unit_of_work:
        updated_permissions_response = []
        owner_change_detected = False

        for perm in changes.permissions:
            update_user = await unit_of_work.user.get_by_username(perm.username)

            # Ensure the current owner isn't changing their role without assigning a new owner
            if update_user.id == user.id and perm.role != Role.OWNER:
                if not any(p.role == Role.OWNER for p in changes.permissions if p.username != user.username):
                    raise BadRequestError(
                        "Operation forbidden: The current owner cannot change own role without reassigning it to another user.",
                    )

            if perm.role:
                if perm.role == Role.OWNER and not owner_change_detected:
                    await unit_of_work.namespace.update(namespace.id, {"owner_id": update_user.id}, update_user)
                    await unit_of_work.namespace.delete_role(namespace.id, update_user.id)
                    owner_change_detected = True
                else:
                    await unit_of_work.namespace.set_role(namespace.id, update_user.id, perm.role)
                updated_permissions_response.append(
                    PermissionResponseItemV1(username=perm.username, role=perm.role),
                )
            else:
                await unit_of_work.namespace.delete_role(namespace.id, update_user.id)

        return PermissionsResponseV1(permissions=updated_permissions_response)

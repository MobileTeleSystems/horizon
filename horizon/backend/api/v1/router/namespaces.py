# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

# mypy: disable-error-code="pydantic-orm"

from fastapi import APIRouter, Depends, HTTPException, status
from typing_extensions import Annotated

from horizon.backend.db.models import NamespaceUserRoleInt, User
from horizon.backend.services import UnitOfWork, current_user
from horizon.commons.errors import get_error_responses
from horizon.commons.exceptions import BadRequestError
from horizon.commons.schemas.v1 import (
    NamespaceCreateRequestV1,
    NamespacePaginateQueryV1,
    NamespaceResponseV1,
    NamespaceUpdateRequestV1,
    NamespaceUserRole,
    PageResponseV1,
    PermissionResponseItemV1,
    PermissionsResponseV1,
    PermissionsUpdateRequestV1,
)

router = APIRouter(prefix="/namespaces", tags=["Namespace"], responses=get_error_responses())


@router.get(
    "/",
    summary="Paginage namespaces",
    dependencies=[Depends(current_user)],
)
async def paginate_namespaces(
    pagination_args: Annotated[NamespacePaginateQueryV1, Depends()],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> PageResponseV1[NamespaceResponseV1]:
    pagination = await unit_of_work.namespace.paginate(**pagination_args.dict())
    return PageResponseV1[NamespaceResponseV1].from_pagination(pagination)


@router.get(
    "/{namespace_id}",
    summary="Get namespace",
    dependencies=[Depends(current_user)],
)
async def get_namespace(
    namespace_id: int,
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> NamespaceResponseV1:
    namespace = await unit_of_work.namespace.get(namespace_id)
    return NamespaceResponseV1.from_orm(namespace)


@router.post(
    "/",
    summary="Create namespace",
    status_code=status.HTTP_201_CREATED,
)
async def create_namespace(
    data: NamespaceCreateRequestV1,
    unit_of_work: Annotated[UnitOfWork, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> NamespaceResponseV1:
    async with unit_of_work:
        namespace = await unit_of_work.namespace.create(**data.dict(), user=user)
        await unit_of_work.namespace_history.create(
            namespace_id=namespace.id,
            data=namespace.to_dict(exclude={"id"}),
        )
    return NamespaceResponseV1.from_orm(namespace)


@router.patch(
    "/{namespace_id}",
    summary="Update namespace",
)
async def update_namespace(
    namespace_id: int,
    changes: NamespaceUpdateRequestV1,
    unit_of_work: Annotated[UnitOfWork, Depends()],
    user: Annotated[User, Depends(current_user)],
) -> NamespaceResponseV1:
    async with unit_of_work:
        await unit_of_work.namespace.check_user_permission(
            user_id=user.id,
            namespace_id=namespace_id,
            required_role=NamespaceUserRoleInt.OWNER,
        )
        namespace = await unit_of_work.namespace.update(
            namespace_id=namespace_id,
            changes=changes.dict(exclude_defaults=True),
            user=user,
        )
        await unit_of_work.namespace_history.create(
            namespace_id=namespace.id,
            data={
                **namespace.to_dict(exclude={"id"}),
                "action": "Updated",
            },
        )
    return NamespaceResponseV1.from_orm(namespace)


@router.delete(
    "/{namespace_id}",
    summary="Delete namespace",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_namespace(
    namespace_id: int,
    user: Annotated[User, Depends(current_user)],
    unit_of_work: Annotated[UnitOfWork, Depends()],
) -> None:
    async with unit_of_work:
        await unit_of_work.namespace.check_user_permission(
            user_id=user.id,
            namespace_id=namespace_id,
            required_role=NamespaceUserRoleInt.OWNER,
        )
        hwm_records = await unit_of_work.hwm.paginate(namespace_id=namespace_id, page=1, page_size=1)
        if hwm_records.total_count:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete namespace because it has related HWM records.",
            )

        namespace = await unit_of_work.namespace.delete(namespace_id=namespace_id, user=user)
        await unit_of_work.namespace_history.create(
            namespace_id=namespace_id,
            data={**namespace.to_dict(exclude={"id"}), "action": "Deleted", "changed_by_user_id": user.id},
        )


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
async def update_namespace_permissions(  # noqa: WPS217
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

        owner_change_detected = False

        for perm in changes.permissions:
            update_user = await unit_of_work.user.get_by_username(perm.username)

            # Ensure the current owner isn't changing their role without assigning a new owner
            if update_user.id == user.id and perm.role != NamespaceUserRole.OWNER:
                if not any(
                    p.role == NamespaceUserRole.OWNER for p in changes.permissions if p.username != user.username
                ):
                    raise BadRequestError("Cannot drop ownership without assigning a new owner.")

            if perm.role:
                if perm.role == NamespaceUserRole.OWNER and not owner_change_detected:
                    await unit_of_work.namespace.set_new_owner(namespace_id, update_user.id)
                    owner_change_detected = True
                else:
                    role_enum = NamespaceUserRoleInt[perm.role.upper()]
                    await unit_of_work.namespace.update_permission(namespace_id, update_user.id, role_enum)
            else:
                await unit_of_work.namespace.delete_permission(namespace_id, update_user.id)

        permissions_dict = await unit_of_work.namespace.get_namespace_users_permissions(namespace_id)
        permissions_response = [
            PermissionResponseItemV1(username=user.username, role=role.name) for user, role in permissions_dict.items()
        ]
        return PermissionsResponseV1(permissions=permissions_response)

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter, Depends
from typing_extensions import Annotated

from horizon.backend.db.models import User
from horizon.backend.services import current_user
from horizon.commons.errors import get_error_responses
from horizon.commons.schemas.v1 import UserResponseV1

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    summary="Get current user info",
    responses=get_error_responses(),
)
async def whoami(
    user: Annotated[User, Depends(current_user)],
) -> UserResponseV1:
    return UserResponseV1.from_orm(user)

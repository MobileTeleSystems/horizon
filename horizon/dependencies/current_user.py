# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from typing import Annotated

from fastapi import Depends, Request

from horizon.db.models.user import User
from horizon.dependencies.stub import Stub
from horizon.providers.auth.base import AuthProvider


async def current_user(
    auth_provider: Annotated[AuthProvider, Depends(Stub(AuthProvider))],
    request: Request,
) -> User:
    return await auth_provider.get_current_user(request)

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing_extensions import Annotated

from horizon.db.models.user import User
from horizon.dependencies.stub import Stub
from horizon.providers.auth.base import AuthProvider

oauth_schema = OAuth2PasswordBearer(tokenUrl="v1/auth/token")


async def current_user(
    auth_provider: Annotated[AuthProvider, Depends(Stub(AuthProvider))],
    auth_schema: Annotated[str, Depends(oauth_schema)],
) -> User:
    return await auth_provider.get_current_user(auth_schema)

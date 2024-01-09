# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing_extensions import Annotated

from horizon.backend.db.models import User
from horizon.backend.dependencies import Stub
from horizon.backend.providers.auth import AuthProvider

oauth_schema = OAuth2PasswordBearer(tokenUrl="v1/auth/token")


async def current_user(
    auth_provider: Annotated[AuthProvider, Depends(Stub(AuthProvider))],
    auth_schema: Annotated[str, Depends(oauth_schema)],
) -> User:
    return await auth_provider.get_current_user(auth_schema)

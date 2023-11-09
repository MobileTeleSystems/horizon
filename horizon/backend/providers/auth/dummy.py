# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import List, Optional, Tuple

from fastapi import Depends
from typing_extensions import Annotated

from horizon.backend.db.models import User
from horizon.backend.dependencies import Stub
from horizon.backend.providers.auth.base import AuthProvider
from horizon.backend.services import UnitOfWork
from horizon.backend.settings import Settings
from horizon.backend.utils.jwt import decode_jwt, sign_jwt
from horizon.commons.exceptions import AuthorizationError


class DummyAuthProvider(AuthProvider):
    def __init__(
        self,
        settings: Annotated[Settings, Depends(Stub(Settings))],
        unit_of_work: Annotated[UnitOfWork, Depends()],
    ) -> None:
        self._settings = settings
        self._uow = unit_of_work

    async def get_current_user(self, access_token: str) -> User:
        if not access_token:
            raise AuthorizationError("Missing auth credentials")

        user_id = self._decode_jwt(access_token)
        user = await self._uow.user.get_by_id(user_id)
        if not user.is_active:
            raise AuthorizationError(f"User {user.username!r} is disabled")
        return user

    async def get_tokens(
        self,
        grant_type: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> Tuple[str, str]:
        if not username or not password:
            raise AuthorizationError("Missing auth credentials")

        async with self._uow:
            user = await self._uow.user.get_or_create(username=username)
        if not user.is_active:
            raise AuthorizationError(f"User {username!r} is disabled")

        access_token = self._sign_jwt(user_id=user.id)
        return access_token, "refresh_token"

    def _sign_jwt(self, user_id: int) -> str:
        return sign_jwt({"user_id": user_id}, self._settings.jwt)

    def _decode_jwt(self, token: str) -> int:
        try:
            payload = decode_jwt(token, self._settings.jwt)
            return int(payload["user_id"])
        except (KeyError, TypeError, ValueError) as e:
            raise AuthorizationError("Invalid token") from e

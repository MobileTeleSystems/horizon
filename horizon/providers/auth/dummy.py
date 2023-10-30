# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from typing import Annotated

from fastapi import Depends

from horizon.db.models.user import User
from horizon.db.repositories.user import UserRepository
from horizon.dependencies import Stub
from horizon.providers.auth.base import AuthProvider
from horizon.settings import Settings
from horizon.utils.jwt import decode_jwt, sign_jwt
from horizon_commons.exceptions.auth import AuthorizationError


class DummyAuthProvider(AuthProvider):
    def __init__(
        self,
        settings: Annotated[Settings, Depends(Stub(Settings))],
        user_repo: Annotated[UserRepository, Depends()],
    ) -> None:
        self._settings = settings
        self._user_repo = user_repo

    async def get_current_user(self, access_token: str) -> User:
        if not access_token:
            raise AuthorizationError("Missing auth credentials")

        user_id = self._decode_jwt(access_token)
        user = await self._user_repo.get_by_id(user_id)
        if not user.is_active:
            raise AuthorizationError(f"User {user.username!r} is disabled")
        return user

    async def get_tokens(
        self,
        grant_type: str,
        username: str | None = None,
        password: str | None = None,
        scopes: list[str] | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> tuple[str, str]:
        if not username or not password:
            raise AuthorizationError("Missing auth credentials")

        user = await self._user_repo.get_or_create(username=username)
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

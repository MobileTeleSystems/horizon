# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer

from app.db.models.user import User
from app.db.repositories.user import UserRepository
from app.dependencies import Stub
from app.exceptions.auth import AuthorizationError
from app.providers.auth.base import AuthProvider
from app.settings import Settings
from app.utils.jwt import decode_jwt, sign_jwt


class DummyAuthProvider(AuthProvider):
    def __init__(
        self,
        settings: Annotated[Settings, Depends(Stub(Settings))],
        user_repo: Annotated[UserRepository, Depends()],
        auth_schema: Annotated[OAuth2PasswordBearer, Depends(Stub(OAuth2PasswordBearer))],
    ) -> None:
        self._settings = settings
        self._user_repo = user_repo
        self._auth_schema = auth_schema

    async def get_current_user(self, request: Request) -> User:
        access_token = await self._auth_schema(request)
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

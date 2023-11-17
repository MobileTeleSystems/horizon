# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import logging
from time import time
from typing import Any, Dict, List, Optional, Tuple

from fastapi import Depends, FastAPI
from typing_extensions import Annotated

from horizon.backend.db.models import User
from horizon.backend.dependencies import Stub
from horizon.backend.providers.auth.base import AuthProvider
from horizon.backend.services import UnitOfWork
from horizon.backend.settings.auth.dummy import DummyAuthProviderSettings
from horizon.backend.utils.jwt import decode_jwt, sign_jwt
from horizon.commons.exceptions.auth import AuthorizationError

log = logging.getLogger(__name__)


class DummyAuthProvider(AuthProvider):
    def __init__(
        self,
        settings: Annotated[DummyAuthProviderSettings, Depends(Stub(DummyAuthProviderSettings))],
        unit_of_work: Annotated[UnitOfWork, Depends()],
    ) -> None:
        self._settings = settings
        self._uow = unit_of_work

    @classmethod
    def setup(cls, app: FastAPI) -> FastAPI:
        settings = DummyAuthProviderSettings.parse_obj(app.state.settings.auth.dict(exclude={"klass"}))
        app.dependency_overrides[AuthProvider] = cls
        app.dependency_overrides[DummyAuthProviderSettings] = lambda: settings
        return app

    async def get_current_user(self, access_token: str) -> User:
        if not access_token:
            raise AuthorizationError("Missing auth credentials")

        user_id = self._get_user_id_from_token(access_token)
        user = await self._uow.user.get_by_id(user_id)
        if not user.is_active:
            raise AuthorizationError(f"User {user.username!r} is disabled")
        return user

    async def get_token(
        self,
        grant_type: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not username or not password:
            raise AuthorizationError("Missing auth credentials")

        log.debug("Get/create user %r in database", username)
        async with self._uow:
            user = await self._uow.user.get_or_create(username=username)

        log.debug("Used with id %r found", user.id)
        if not user.is_active:
            raise AuthorizationError(f"User {username!r} is disabled")

        log.debug("Generate access token for user id %r", user.id)
        access_token, expires_at = self._generate_access_token(user_id=user.id)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_at": expires_at,
        }

    def _generate_access_token(self, user_id: int) -> Tuple[str, float]:
        expires_at = time() + self._settings.access_token.expire_seconds
        payload = {
            "user_id": user_id,
            "exp": expires_at,
        }
        access_token = sign_jwt(
            payload,
            self._settings.access_token.secret_key,
            self._settings.access_token.security_algorithm,
        )
        return access_token, expires_at

    def _get_user_id_from_token(self, token: str) -> int:
        try:
            payload = decode_jwt(
                token,
                self._settings.access_token.secret_key,
                self._settings.access_token.security_algorithm,
            )
            return int(payload["user_id"])
        except (KeyError, TypeError, ValueError) as e:
            raise AuthorizationError("Invalid token") from e

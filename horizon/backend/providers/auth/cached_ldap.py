# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

"""
AuthProvider using LDAP, but
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from bonsai.asyncio import AIOConnectionPool
from devtools import pformat
from fastapi import Depends, FastAPI
from passlib.ifc import PasswordHash
from passlib.registry import get_crypt_handler
from typing_extensions import Annotated

from horizon.backend.dependencies import Stub
from horizon.backend.providers.auth.base import AuthProvider
from horizon.backend.providers.auth.ldap import LDAPAuthProvider
from horizon.backend.services import UnitOfWork
from horizon.backend.settings import Settings
from horizon.backend.settings.auth.cached_ldap import CashedLDAPAuthProviderSettings
from horizon.commons.exceptions import AuthorizationError

log = logging.getLogger(__name__)


class CashedLDAPAuthProvider(LDAPAuthProvider):
    def __init__(
        self,
        settings: Annotated[Settings, Depends(Stub(Settings))],
        auth_settings: Annotated[CashedLDAPAuthProviderSettings, Depends(Stub(CashedLDAPAuthProviderSettings))],
        pool: Annotated[Optional[AIOConnectionPool], Depends(Stub(AIOConnectionPool))],
        unit_of_work: Annotated[UnitOfWork, Depends()],
    ) -> None:
        self._pool: Optional[AIOConnectionPool] = pool
        self._settings: Settings = settings
        self._auth_settings: CashedLDAPAuthProviderSettings = auth_settings
        self._uow: UnitOfWork = unit_of_work

    @classmethod
    def setup(cls, app: FastAPI) -> FastAPI:
        settings = CashedLDAPAuthProviderSettings.parse_obj(app.state.settings.auth.dict(exclude={"provider"}))
        log.info("Using %s provider with settings:\n%s", cls.__name__, pformat(settings))
        app.dependency_overrides[AuthProvider] = cls
        app.dependency_overrides[CashedLDAPAuthProviderSettings] = lambda: settings

        # lookup uses the same connection pool for all users
        pool = cls.get_lookup_pool(settings.ldap)
        app.dependency_overrides[AIOConnectionPool] = lambda: pool
        return app

    async def get_token(
        self,
        grant_type: Optional[str] = None,
        login: Optional[str] = None,
        password: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not login or not password:
            raise AuthorizationError("Missing auth credentials")

        # firstly check if user credentials already exists in cache
        username = await self._resolve_username_from_credentials_cache(login, password)
        if not username:
            username = await self._resolve_username_from_ldap(login, password)

        log.info("Get/create user %r in database", username)
        async with self._uow:
            # and only then create user in database.
            # avoid creating fake users by spamming auth endpoint
            user = await self._uow.user.get_or_create(username=username)

            log.info("User id %r found", user.id)
            if not user.is_active:
                # TODO: check if user is locked in LDAP
                raise AuthorizationError(f"User {username!r} is disabled")

            log.info("Update credentials cache for user id %r", user.id)
            await self._update_credentials_cache(user_id=user.id, login=login, password=password)

        log.info("Generate access token for user id %r", user.id)
        access_token, expires_at = self._generate_access_token(user)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_at": expires_at,
        }

    def _get_hasher(self) -> PasswordHash:
        hashing_settings = self._auth_settings.cache.password_hash
        handler = get_crypt_handler(hashing_settings.algorithm)
        return handler.using(**hashing_settings.options)

    async def _resolve_username_from_credentials_cache(self, login: str, password: str) -> Optional[str]:
        log.info("Perform lookup in credentials cache")
        user_cache = await self._uow.credentials_cache.get_by_login(login)
        if not user_cache:
            log.info("User %r not found in cache", login)
            return None

        log.debug("Found item %r", user_cache)
        expiration_date = user_cache.updated_at + timedelta(seconds=self._auth_settings.cache.expire_seconds)
        if expiration_date < datetime.now(tz=timezone.utc):
            log.info("Cache item expired")
            return None

        hasher = self._get_hasher()
        if not hasher.verify(password, user_cache.password_hash):
            raise AuthorizationError("Wrong credentials")

        log.info("Credentials match the cache")
        return user_cache.user.username

    async def _update_credentials_cache(self, user_id: int, login: str, password: str) -> None:
        # this is not a dedicated method of repository because we need hashing settings to generate password hash,
        # and generating new hash every time is expensive
        hasher = self._get_hasher()
        user_cache = await self._uow.credentials_cache.get_by_login(login=login)

        data: Dict[str, Any] = {}
        if not user_cache or user_cache.user_id != user_id:
            data["user_id"] = user_id
        if not user_cache or not hasher.verify(password, user_cache.password_hash):
            data["password_hash"] = hasher.encrypt(password)

        # even if nothing is changed in credentials cache, we do perform an update to sync `updated_at` column
        await self._uow.credentials_cache.create_or_update(login=login, data=data)

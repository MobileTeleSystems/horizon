# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

"""
AuthProvider using LDAP for checking user existence and credentials.

Based on `ldap3 <https://ldap3.readthedocs.io>`_

Similar to:
* `JupyterHub LDAPAuthenticator <https://github.com/jupyterhub/ldapauthenticator>`_
* `Flask-AppBuilder LDAP integration <https://github.com/dpgaspar/Flask-AppBuilder/blob/master/docs/config.rst>`_, used in Apache Airflow
"""

import asyncio
import logging
from time import time
from typing import Any, Dict, List, Optional, Tuple

from fastapi import Depends, FastAPI
from ldap3 import ALL_ATTRIBUTES, Connection, ServerPool
from ldap3.core.exceptions import LDAPExceptionError
from typing_extensions import Annotated

from horizon.backend.db.models import User
from horizon.backend.dependencies import Stub
from horizon.backend.providers.auth.base import AuthProvider
from horizon.backend.services import UnitOfWork
from horizon.backend.settings import Settings
from horizon.backend.settings.auth.ldap import (
    LDAPAuthProviderSettings,
    LDAPLookupSettings,
)
from horizon.backend.utils.jwt import decode_jwt, sign_jwt
from horizon.commons.exceptions.auth import AuthorizationError
from horizon.commons.exceptions.entity import EntityNotFoundError
from horizon.commons.exceptions.setup import SetupError

log = logging.getLogger(__name__)


class LDAPAuthProvider(AuthProvider):
    def __init__(
        self,
        settings: Annotated[Settings, Depends(Stub(Settings))],
        auth_settings: Annotated[LDAPAuthProviderSettings, Depends(Stub(LDAPAuthProviderSettings))],
        pool: Annotated[ServerPool, Depends(Stub(ServerPool))],
        unit_of_work: Annotated[UnitOfWork, Depends()],
    ) -> None:
        self._pool = pool
        self._settings = settings
        self._auth_settings = auth_settings
        self._uow = unit_of_work

    @classmethod
    def setup(cls, app: FastAPI) -> FastAPI:
        settings = LDAPAuthProviderSettings.parse_obj(app.state.settings.auth)
        server_settings = settings.ldap.server
        pool = ServerPool(
            [str(url) for url in server_settings.urls],
            pool_strategy=server_settings.strategy,
            active=server_settings.retries,  # type: ignore[arg-type]
            exhaust=server_settings.lost_timeout,  # type: ignore[arg-type]
        )

        app.dependency_overrides[AuthProvider] = cls
        app.dependency_overrides[LDAPAuthProviderSettings] = lambda: settings
        app.dependency_overrides[ServerPool] = lambda: pool
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

        # firstly check if user exists in LDAP and credentials are valid
        loop = asyncio.get_running_loop()
        lookup = self._auth_settings.ldap.lookup
        if lookup:
            log.debug("Looking up user %r in LDAP", username)
            dn, real_username = await loop.run_in_executor(None, self._lookup_user, username, lookup)
        else:
            dn = self._auth_settings.ldap.bind_dn_template.format(
                username=username,
                base_dn=self._auth_settings.ldap.base_dn,
                uid_attribute=self._auth_settings.ldap.uid_attribute,
            )
            real_username = username
        log.debug("Check user credentials %r in LDAP", dn)
        await loop.run_in_executor(None, self._login, dn, password)

        log.debug("Get/create user %r in database", real_username)
        async with self._uow:
            # and only then create user in database.
            # avoid creating fake users by spamming auth endpoint
            user = await self._uow.user.get_or_create(username=real_username)

        log.debug("Used id %r found", user.id)
        if not user.is_active:
            # TODO: check if user is locked in LDAP
            raise AuthorizationError(f"User {real_username!r} is disabled")

        log.debug("Generate access token for user id %r", user.id)
        access_token, expires_at = self._generate_access_token(user_id=user.id)
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_at": expires_at,
        }

    def _get_connection(self, **kwargs) -> Connection:
        # TODO: use some kind of connection pool, probably with REUSABLE strategy
        return Connection(
            self._pool,
            read_only=True,
            **kwargs,
        )

    def _lookup_user(self, username: str, options: LDAPLookupSettings) -> Tuple[str, str]:
        # Reference implementations:
        # https://github.com/dpgaspar/Flask-AppBuilder/blob/2c5763371b81cd679d88b9971ba5d1fc4d71d54b/flask_appbuilder/security/manager.py#L902
        # https://github.com/jupyterhub/ldapauthenticator/blob/main/ldapauthenticator/ldapauthenticator.py
        if options.credentials:
            connection = self._get_connection(
                user=options.credentials.user,
                password=options.credentials.password.get_secret_value(),
                pool_name="lookup",
            )
        else:
            connection = self._get_connection(pool_name="lookup")

        query = options.query.format(username=username, uid_attribute=self._auth_settings.ldap.uid_attribute)

        try:
            if not connection.bind():
                log.debug("Error from LDAP: %s", connection.last_error)
                raise SetupError("Wrong LDAP credentials")

            if connection.search(
                search_base=self._auth_settings.ldap.base_dn,
                search_filter=query,
                search_scope=options.scope,
                attributes=[ALL_ATTRIBUTES],
                size_limit=1,
            ):
                entry = connection.entries[0]
                log.debug("Found entry:\n%s", entry)
                uid = entry.entry_attributes_as_dict[self._auth_settings.ldap.uid_attribute][0]
                return entry.entry_dn, uid
        finally:
            connection.unbind()

        raise EntityNotFoundError("User", "username", username)

    def _login(self, username: str, password: str):
        connection = self._get_connection(
            user=username,
            password=password,
        )
        try:
            if not connection.bind():
                log.debug("Error from LDAP: %s", connection.last_error)
                details = None
                if self._settings.server.debug:
                    # don't print error details in production
                    details = connection.last_error
                raise AuthorizationError("Wrong credentials", details=details)
        except LDAPExceptionError as e:
            details = None
            if self._settings.server.debug:
                # don't print error details in production
                details = connection.last_error
            raise AuthorizationError("Wrong credentials", details=details) from e
        finally:
            connection.unbind()

    def _generate_access_token(self, user_id: int) -> Tuple[str, float]:
        expires_at = time() + self._auth_settings.access_token.expire_seconds
        payload = {
            "user_id": user_id,
            "exp": expires_at,
        }
        access_token = sign_jwt(
            payload,
            self._auth_settings.access_token.secret_key,
            self._auth_settings.access_token.security_algorithm,
        )
        return access_token, expires_at

    def _get_user_id_from_token(self, token: str) -> int:
        try:
            payload = decode_jwt(
                token,
                self._auth_settings.access_token.secret_key,
                self._auth_settings.access_token.security_algorithm,
            )
            return int(payload["user_id"])
        except (KeyError, TypeError, ValueError) as e:
            raise AuthorizationError("Invalid token") from e

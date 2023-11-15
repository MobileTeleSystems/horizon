# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

"""
AuthProvider using LDAP for checking user existence and credentials.

Based on `bonsai <https://github.com/noirello/bonsai>`_

Similar to:
* `JupyterHub LDAPAuthenticator <https://github.com/jupyterhub/ldapauthenticator>`_
* `Flask-AppBuilder LDAP integration <https://github.com/dpgaspar/Flask-AppBuilder/blob/master/docs/config.rst>`_, used in Apache Airflow
"""

import logging
from time import time
from typing import Any, Dict, List, Optional, Tuple

from bonsai import InvalidDN, LDAPClient
from bonsai.asyncio import AIOConnectionPool
from bonsai.errors import AuthenticationError, LDAPError
from fastapi import Depends, FastAPI
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
        pool: Annotated[Optional[AIOConnectionPool], Depends(Stub(AIOConnectionPool))],
        unit_of_work: Annotated[UnitOfWork, Depends()],
    ) -> None:
        self._pool = pool
        self._settings = settings
        self._auth_settings = auth_settings
        self._uow = unit_of_work

    @classmethod
    def setup(cls, app: FastAPI) -> FastAPI:
        settings = LDAPAuthProviderSettings.parse_obj(app.state.settings.auth.dict(exclude={"klass"}))
        app.dependency_overrides[AuthProvider] = cls
        app.dependency_overrides[LDAPAuthProviderSettings] = lambda: settings
        app.dependency_overrides[AIOConnectionPool] = lambda: None

        if settings.ldap.lookup:
            # lookup uses the same connection pool for all users
            client = LDAPClient(str(settings.ldap.url))
            if settings.ldap.lookup.credentials:
                client.set_credentials(
                    settings.ldap.auth_mechanism,
                    settings.ldap.lookup.credentials.user,
                    settings.ldap.lookup.credentials.password.get_secret_value(),
                )
            client.connect()  # test connection during start

            pool = AIOConnectionPool(
                client,
                minconn=settings.ldap.pool.initial,
                maxconn=settings.ldap.pool.max,
            )
            app.dependency_overrides[AIOConnectionPool] = lambda: pool
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
        lookup = self._auth_settings.ldap.lookup
        if lookup:
            log.debug("Looking up user %r in LDAP", username)
            dn, real_username = await self._lookup_user(username, lookup)
        else:
            dn = self._auth_settings.ldap.bind_dn_template.format(
                username=username,
                base_dn=self._auth_settings.ldap.base_dn,
                uid_attribute=self._auth_settings.ldap.uid_attribute,
            )
            real_username = username
        log.debug("Check user credentials %r in LDAP", dn)
        await self._login(dn, password)

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

    async def _lookup_user(self, username: str, options: LDAPLookupSettings) -> Tuple[str, str]:
        # Reference implementations:
        # https://github.com/dpgaspar/Flask-AppBuilder/blob/2c5763371b81cd679d88b9971ba5d1fc4d71d54b/flask_appbuilder/security/manager.py#L902
        # https://github.com/jupyterhub/ldapauthenticator/blob/main/ldapauthenticator/ldapauthenticator.py
        query = options.query.format(username=username, uid_attribute=self._auth_settings.ldap.uid_attribute)

        pool: AIOConnectionPool = self._pool  # type: ignore[assignment]
        try:
            async with pool.spawn() as connection:
                results = await connection.search(
                    base=self._auth_settings.ldap.base_dn,
                    scope=options.scope,
                    filter_exp=query,
                    attrlist=["*"],
                    sizelimit=1,
                )
                if results:
                    entry = results[0]
                    log.debug("Found entry:\n%s", entry)
                    dn = str(entry["dn"])
                    uid = entry[self._auth_settings.ldap.uid_attribute][0]
                    return dn, uid
        except LDAPError as e:
            raise SetupError("Wrong LDAP settings") from e

        raise EntityNotFoundError("User", "username", username)

    async def _login(self, username: str, password: str):
        client = LDAPClient(str(self._auth_settings.ldap.url))
        client.set_credentials(self._auth_settings.ldap.auth_mechanism, username, password)
        try:
            async with client.connect(is_async=True) as connection:
                await connection.whoami()
        except (AuthenticationError, InvalidDN) as e:
            raise AuthorizationError("Wrong credentials") from e

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

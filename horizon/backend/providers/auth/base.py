# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from fastapi import FastAPI

from horizon.backend.db.models import User


class AuthProvider(ABC):
    """Basic class for all Auth providers.

    Constructor is called by FastAPI, and can use Dependency injection mechanism.
    See :obj:`~setup` for more details.
    """

    @classmethod
    @abstractmethod
    def setup(cls, app: FastAPI) -> FastAPI:
        """
        This method is called by :obj:`horizon.backend.application_factory`.

        Here you should add dependency overrides for auth provider,
        and return new ``app`` object.

        Examples
        --------

        .. code-block::

            from fastapi import FastAPI
            from my_awesome_auth_provider.settings import MyAwesomeAuthProviderSettings
            from horizon.backend.dependencies import Stub

            class MyAwesomeAuthProvider(AuthProvider):
                def setup(app):
                    app.dependency_overrides[AuthProvider] = MyAwesomeAuthProvider

                    # `settings_object_factory` returns MyAwesomeAuthProviderSettings object
                    app.dependency_overrides[MyAwesomeAuthProviderSettings] = settings_object_factory
                    return app

                def __init__(
                    self,
                    settings: Annotated[MyAwesomeAuthProviderSettings, Depends(Stub(MyAwesomeAuthProviderSettings))],
                ):
                    # settings object is set automatically by FastAPI's dependency_overrides
                    self.settings = settings
        """
        ...

    @abstractmethod
    async def get_current_user(self, access_token: str) -> User:
        """
        This method should return currently logged in user.

        Parameters
        ----------
        access_token : str
            JWT token got from ``Authorization: Bearer <token>`` header.

        Returns
        -------
        :obj:`horizon.backend.db.models.User`
            Current user object
        """
        ...

    @abstractmethod
    async def get_token(
        self,
        grant_type: Optional[str] = None,
        login: Optional[str] = None,
        password: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        This method should perform authentication and return JWT token.

        Parameters
        ----------
        See:
          * https://auth0.com/docs/get-started/authentication-and-authorization-flow/call-your-api-using-resource-owner-password-flow
          * https://connect2id.com/products/server/docs/api/token

        Returns
        -------
        Dict:
            .. code-block:: python

                {
                    "access_token": "some.jwt.token",
                    "token_type": "bearer",
                    "expires_in": 3600,
                }
        """
        ...

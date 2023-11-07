# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from typing import Optional
from urllib.parse import urlparse

from pydantic import AnyHttpUrl, BaseModel, SecretStr
from typing_extensions import Literal

from horizon_client.auth.base import BaseAuth


class OAuth2Password(BaseAuth, BaseModel):
    """Authorization using OAuth2 + ``grant_type=password``.

    Resulting access is passed in ``Authorization: Bearer ${token}`` header.
    Tokens can be refreshed.

    Parameters
    ----------
    username : str
        User name

    password : str
        User password

    token_endpoint : str, optional
        Custom URL for OAuth2 ``/token`` endpoint.

    Examples
    --------

    .. code-block:: python

        from horizon_client.auth import OAuth2Password

        auth = OAuth2Password(username="me", password="12345")
    """

    username: str
    password: SecretStr
    token_endpoint: Optional[AnyHttpUrl] = None

    type: Literal["oauth2_password"] = "oauth2_password"

    def patch_session(self, session):
        return session

    def fetch_token_kwargs(self, base_url: AnyHttpUrl) -> dict[str, str]:
        url: str | None = self.token_endpoint
        if not url:
            # default path for token
            parsed_url = urlparse(base_url)
            token_url = parsed_url._replace(path=parsed_url.path + "/v1/auth/token")  # noqa: WPS437, WPS336
            url = token_url.geturl()

        return {
            "url": str(url),
            "username": self.username,
            "password": self.password.get_secret_value(),
        }

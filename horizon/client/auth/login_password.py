# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from urllib.parse import urlparse

from pydantic import AnyHttpUrl, BaseModel, SecretStr
from typing_extensions import Literal

from horizon.client.auth.base import BaseAuth


class LoginPassword(BaseAuth, BaseModel):
    """Authorization using OAuth2 + ``grant_type=password``.

    Resulting access is passed in ``Authorization: Bearer ${token}`` header.
    Tokens can be refreshed.

    Parameters
    ----------
    username : str
        User name

    password : str
        User password

    Examples
    --------

    >>> from horizon.client.auth import LoginPassword
    >>> auth = LoginPassword(login="me", password="12345")
    """

    login: str
    password: SecretStr

    type: Literal["login_password"] = "login_password"

    def patch_session(self, session):
        return session

    def fetch_token_kwargs(self, base_url: AnyHttpUrl) -> dict[str, str]:
        # default path for token
        parsed_url = urlparse(str(base_url))
        token_url = parsed_url._replace(path=parsed_url.path + "/v1/auth/token")  # noqa: WPS437, WPS336
        url = token_url.geturl()

        return {
            "url": str(url),
            "username": self.login,
            "password": self.password.get_secret_value(),
        }

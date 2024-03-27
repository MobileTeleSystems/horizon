# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from authlib.oauth2.auth import OAuth2Token as AuthlibToken
from jose import ExpiredSignatureError, jwt
from pydantic import AnyHttpUrl, BaseModel, validator
from typing_extensions import Literal

from horizon.client.auth.base import BaseAuth, Session


class AccessToken(BaseAuth, BaseModel):
    """Authorization using access token.

    Token is passed in ``Authorization: Bearer ${token}`` header,
    and does not support refreshing.

    Parameters
    ----------
    token: str
        Access token

    Examples
    --------

    >>> from horizon.client.auth import AccessToken
    >>> auth = AccessToken(token="my.access.token")
    """

    token: str

    type: Literal["access_token"] = "access_token"

    def patch_session(self, session: Session) -> Session:
        if session.token:
            return session

        # https://github.com/lepture/authlib/issues/600
        token_decoded = jwt.decode(self.token, key="NONE", options={"verify_signature": False})
        session.token = AuthlibToken.from_dict(
            {
                "access_token": self.token,
                "token_type": "Bearer",
                "expires_at": token_decoded["exp"],
            },
        )
        return session

    def fetch_token_kwargs(self, base_url: AnyHttpUrl) -> dict[str, str]:
        return {}

    @validator("token")
    def _validate_token(cls, value):
        token_decoded = jwt.decode(value, key="NONE", options={"verify_signature": False})
        if "exp" not in token_decoded:
            raise ExpiredSignatureError("Missing expiration time in token")
        return value

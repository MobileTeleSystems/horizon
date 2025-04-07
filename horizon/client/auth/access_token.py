# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

from authlib.jose import JWTClaims, jwt
from authlib.jose.errors import BadSignatureError, ExpiredTokenError
from authlib.oauth2.auth import OAuth2Token as AuthlibToken  # type: ignore[attr-defined]
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

        # AuthlibToken expiration is optional, and JWT token is not parsed.
        # We have to extract expiration time manually.
        claims = self._parse_token(self.token)
        session.token = AuthlibToken.from_dict(
            {
                "access_token": self.token,
                "token_type": "Bearer",
                "expires_at": claims["exp"],
            },
        )
        return session

    def fetch_token_kwargs(self, base_url: AnyHttpUrl) -> dict[str, str]:
        return {}

    @classmethod
    def _parse_token(cls, token) -> JWTClaims:
        try:
            # As client don't have private key used for signing JWT, this call will always raise this exception
            # https://github.com/lepture/authlib/issues/600
            jwt.decode(token, key="")
        except BadSignatureError as e:
            token_decoded = e.result.payload
            claims = JWTClaims(
                header=token_decoded,
                payload=token_decoded,
            )

        if "exp" not in claims:
            msg = "Missing expiration time in token"
            raise ExpiredTokenError(msg)

        claims.validate()
        return claims

    @validator("token")
    def _validate_access_token(cls, value):  # noqa: N805
        # AuthlibToken doesn't perform any validation, so we have to
        cls._parse_token(value)
        return value

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import time

from jose import JWTError, jwt

from horizon.backend.settings.jwt import JWTSettings
from horizon.commons.exceptions.auth import AuthorizationError
from horizon.commons.exceptions.setup import SetupError


def sign_jwt(payload: dict, settings: JWTSettings) -> str:
    if not settings.secret_key:
        raise SetupError("Expected settings.jwt.secret_key to be set, got None")

    real_payload = {
        "exp": time.time() + settings.token_expired_seconds,
        **payload,
    }
    return jwt.encode(
        real_payload,
        settings.secret_key,
        algorithm=settings.security_algorithm,
    )


def decode_jwt(token: str, settings: JWTSettings) -> dict:
    if not settings.secret_key:
        raise SetupError("Expected settings.jwt.secret_key to be set, got None")

    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.security_algorithm],
        )
    except JWTError as e:
        raise AuthorizationError("Invalid token") from e

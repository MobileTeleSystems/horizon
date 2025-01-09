# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from authlib.jose import JsonWebToken
from authlib.jose.errors import ExpiredTokenError, JoseError

from horizon.commons.exceptions import AuthorizationError


def sign_jwt(payload: dict, secret_key: str, security_algorithm: str) -> str:
    jwt = JsonWebToken([security_algorithm])
    return jwt.encode(
        header={"alg": security_algorithm},
        payload=payload,
        key=secret_key,
    ).decode("utf-8")


def decode_jwt(token: str, secret_key: str, security_algorithm: str) -> dict:
    try:
        result = JsonWebToken([security_algorithm]).decode(token, key=secret_key)
        if "exp" not in result:
            raise ExpiredTokenError("Missing expiration time in token")

        result.validate()

        return result
    except JoseError as e:
        raise AuthorizationError("Invalid token") from e

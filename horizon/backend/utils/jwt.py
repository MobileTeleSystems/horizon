# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from jose import ExpiredSignatureError, JWTError, jwt

from horizon.commons.exceptions import AuthorizationError


def sign_jwt(payload: dict, secret_key: str, security_algorithm: str) -> str:
    return jwt.encode(
        payload,
        secret_key,
        algorithm=security_algorithm,
    )


def decode_jwt(token: str, secret_key: str, security_algorithm: str) -> dict:
    try:
        result = jwt.decode(
            token,
            secret_key,
            algorithms=[security_algorithm],
        )
        if "exp" not in result:
            raise ExpiredSignatureError("Missing expiration time in token")

        return result
    except JWTError as e:
        raise AuthorizationError("Invalid token") from e

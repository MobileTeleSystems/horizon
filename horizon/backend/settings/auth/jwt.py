# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import textwrap

from pydantic import BaseModel, Field


class JWTSettings(BaseModel):
    secret_key: str = Field(
        description=textwrap.dedent(
            """
            Secret key for signing JWT tokens.

            Can be any string. It is recommended to generate random value for every application instance.
            """,
        ),
    )
    security_algorithm: str = Field(
        default="HS256",
        description=textwrap.dedent(
            """
            Algorithm used for signing JWT tokens.

            See `python-jose <https://python-jose.readthedocs.io/en/latest/jws/index.html#supported-algorithms>`_
            documentation.
            """,
        ),
    )
    expire_seconds: int = Field(
        default=10 * 60 * 60,
        description="Token expiration time, in seconds",
    )

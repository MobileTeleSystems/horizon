# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

import textwrap

from pydantic import BaseModel, Field, SecretStr


class JWTSettings(BaseModel):
    """Settings related to JWT tokens.

    Examples
    --------

    .. code-block:: bash

        HORIZON__AUTH__ACCESS_KEY__SECRET_KEY=somesecret
        HORIZON__AUTH__ACCESS_KEY__EXPIRE_SECONDS=3600  # 1 hour
    """

    secret_key: SecretStr = Field(
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

            See `authlib <https://docs.authlib.org/en/latest/specs/rfc7518.html>`_
            documentation.
            """,
        ),
    )
    expire_seconds: int = Field(
        default=10 * 60 * 60,
        description="Token expiration time, in seconds",
    )

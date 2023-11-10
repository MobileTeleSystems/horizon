# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import textwrap

from pydantic import BaseModel, Field


class DatabaseSettings(BaseModel):
    """Database connection settings.

    You can pass here any option supported by
    `SQLAlchemy Engine class <https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine>`_.
    """

    url: str = Field(
        description=textwrap.dedent(  # noqa: WPS462
            """
            Database connection URL.

            See `SQLAlchemy documentation <https://docs.sqlalchemy.org/en/20/core/engines.html#backend-specific-urls>`_

            .. warning:

                Only async drivers are supported, e.g. ``asyncpg``
            """,
        ),
    )

    class Config:
        extra = "allow"

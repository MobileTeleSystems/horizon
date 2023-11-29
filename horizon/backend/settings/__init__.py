# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import Field

BaseSettings: type
try:
    from pydantic import BaseSettings  # type: ignore[no-redef] # noqa: WPS440
except ImportError:
    from pydantic_settings import BaseSettings  # type: ignore[no-redef] # noqa: WPS440

from horizon.backend.settings.auth import AuthSettings
from horizon.backend.settings.database import DatabaseSettings
from horizon.backend.settings.server import ServerSettings


class Settings(BaseSettings):
    """Horizon backend settings.

    Backend can be configured in 2 ways:

    * By explicitly passing ``settings`` object as an argument to :obj:`application_factory <horizon.backend.main.application_factory>`
    * By setting up environment variables matching a specific key.

        All environment variable names are written in uppercase and should be prefixed with ``HORIZON__``.
        Nested items are delimited with ``__``.

    More details can be found in `Pydantic documentation <https://docs.pydantic.dev/latest/concepts/pydantic_settings/>`_.

    Examples
    --------

    .. code-block:: bash

        # same as settings.database.url = "postgresql+asyncpg://postgres:postgres@localhost:5432/horizon"
        HORIZON__DATABASE__URL=postgresql+asyncpg://postgres:postgres@localhost:5432/horizon

        # same as settings.server.debug = True
        HORIZON__SERVER__DEBUG=True

        # same as settings.auth.provider = horizon.backend.providers.auth.dummy.DummyAuthProvider
        HORIZON__AUTH__PROVIDER=horizon.backend.providers.auth.dummy.DummyAuthProvider
    """

    database: DatabaseSettings = Field(description=":ref:`Database settings <backend-configuration-database>`")
    server: ServerSettings = Field(
        default_factory=ServerSettings,
        description=":ref:`Server settings <backend-configuration>`",
    )
    auth: AuthSettings = Field(
        default_factory=AuthSettings,
        description=":ref:`Auth setting <backend-auth-providers>`",
    )

    class Config:
        env_prefix = "HORIZON__"
        env_nested_delimiter = "__"

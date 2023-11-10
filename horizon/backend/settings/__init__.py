# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseSettings, Field

from horizon.backend.settings.auth import AuthProviderSettings
from horizon.backend.settings.database import DatabaseSettings
from horizon.backend.settings.server import ServerSettings


class Settings(BaseSettings):
    database: DatabaseSettings
    server: ServerSettings = Field(default_factory=ServerSettings)
    auth: AuthProviderSettings = Field(default_factory=AuthProviderSettings)

    class Config:
        env_prefix = "HORIZON_"
        env_nested_delimiter = "__"

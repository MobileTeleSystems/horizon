# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseSettings, Field

from horizon.backend.settings.auth import AuthSettings
from horizon.backend.settings.database import DatabaseSettings
from horizon.backend.settings.server import ServerSettings


class Settings(BaseSettings):
    database: DatabaseSettings
    server: ServerSettings = Field(default_factory=ServerSettings)
    auth: AuthSettings

    class Config:
        env_prefix = "HORIZON_"
        env_nested_delimiter = "__"

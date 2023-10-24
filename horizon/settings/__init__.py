# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseSettings, Field

from horizon.settings.auth import AuthSettings
from horizon.settings.database import DatabaseSettings
from horizon.settings.jwt import JWTSettings
from horizon.settings.server import ServerSettings


class Settings(BaseSettings):
    database: DatabaseSettings
    server: ServerSettings = Field(default_factory=ServerSettings)
    auth: AuthSettings = Field(default_factory=AuthSettings)
    jwt: JWTSettings = Field(default_factory=JWTSettings)

    class Config:
        env_prefix = "HORIZON_"
        env_nested_delimiter = "__"

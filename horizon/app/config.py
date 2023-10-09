# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_URL: str

    DEBUG: bool = True

    class Config:
        env_prefix = "HORIZON_"

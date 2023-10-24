# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import json

from pydantic import BaseModel, Field, validator


class DatabaseSettings(BaseModel):
    url: str
    engine_args: dict = Field(default_factory=dict)

    @validator("engine_args", pre=True)
    def _validate_engine_args(cls, value) -> dict:
        if isinstance(value, str):
            return json.loads(value)
        return value

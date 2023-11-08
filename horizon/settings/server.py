# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import List, Set

from pydantic import BaseModel, Field


class CorsSettings(BaseModel):
    enabled: bool = True
    allow_origins: List[str] = ["*"]
    allow_credentials: bool = True
    allow_methods: List[str] = ["*"]
    allow_headers: List[str] = ["*"]

    class Config:
        extra = "allow"


class PrometheusSettings(BaseModel):
    enabled: bool = True
    group_paths: bool = True
    skip_paths: Set[str] = Field(default_factory=set)

    class Config:
        extra = "allow"


class ServerSettings(BaseModel):
    debug: bool = False

    cors: CorsSettings = Field(default_factory=CorsSettings)
    prometheus: PrometheusSettings = Field(default_factory=PrometheusSettings)

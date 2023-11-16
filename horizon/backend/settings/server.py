# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import List, Set

from pydantic import BaseModel, Field

from horizon.backend.settings.log import LoggingSettings


class CorsSettings(BaseModel):
    """CORS Middleware Settings.

    See `CORSMiddleware <https://www.starlette.io/middleware/#corsmiddleware>`_ documentation.
    """

    enabled: bool = True
    allow_origins: List[str] = []
    allow_credentials: bool = False
    allow_methods: List[str] = ["GET"]
    # https://github.com/snok/asgi-correlation-id#cors
    allow_headers: List[str] = ["X-Request-ID", "X-Request-With"]
    expose_headers: List[str] = ["X-Request-ID"]

    class Config:
        extra = "allow"


class PrometheusSettings(BaseModel):
    """Prometheus Middleware Settings.

    See `starlette-exporter <https://github.com/stephenhillier/starlette_exporter#options>`_ documentation.
    """

    enabled: bool = True
    skip_paths: Set[str] = set()
    skip_methods: Set[str] = {"OPTIONS"}
    # These will be new defaults in starlette-exporter 0.18:
    # https://github.com/stephenhillier/starlette_exporter/issues/79
    group_paths: bool = True
    filter_unhandled_paths: bool = True

    class Config:
        extra = "allow"


class RequestIDSettings(BaseModel):
    """X-Request-ID Middleware Settings.

    See `asgi-correlation-id <https://github.com/snok/asgi-correlation-id>`_ documentation.
    """

    enabled: bool = True
    header_name: str = "X-Request-ID"
    update_request_header = False


class ServerSettings(BaseModel):
    debug: bool = Field(
        default=False,
        description="Enable debug output in responses. Do not use this on production!",
    )
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    cors: CorsSettings = Field(default_factory=CorsSettings)
    prometheus: PrometheusSettings = Field(default_factory=PrometheusSettings)
    request_id: RequestIDSettings = Field(default_factory=RequestIDSettings)

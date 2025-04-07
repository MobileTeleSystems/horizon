# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

import json
from typing import Any, List

from pydantic import BaseModel, Field, validator


class CORSSettings(BaseModel):
    """CORS Middleware Settings.

    See `CORSMiddleware <https://www.starlette.io/middleware/#corsmiddleware>`_ documentation.

    .. note::

        You can pass here any extra option supported by ``CORSMiddleware``,
        even if it is not mentioned in documentation.

    Examples
    --------

    For development environment:

    .. code-block:: bash

        HORIZON__SERVER__CORS__ENABLED=True
        HORIZON__SERVER__CORS__ALLOW_ORIGINS="*"
        HORIZON__SERVER__CORS__ALLOW_METHODS="*"
        HORIZON__SERVER__CORS__ALLOW_HEADERS="*"
        HORIZON__SERVER__CORS__EXPOSE_HEADERS=X-Request-ID,Location,Access-Control-Allow-Credentials

    For production environment:

    .. code-block:: bash

        HORIZON__SERVER__CORS__ENABLED=True
        HORIZON__SERVER__CORS__ALLOW_ORIGINS="production.example.com"
        HORIZON__SERVER__CORS__ALLOW_METHODS="GET"
        HORIZON__SERVER__CORS__ALLOW_HEADERS="X-Request-ID,X-Request-With"
        HORIZON__SERVER__CORS__EXPOSE_HEADERS="X-Request-ID"
        # custom option passed directly to middleware
        HORIZON__SERVER__CORS__MAX_AGE=600
    """

    enabled: bool = Field(default=True, description="Set to ``True`` to enable middleware")
    allow_origins: List[str] = Field(default_factory=list, description="Domains allowed for CORS")
    allow_credentials: bool = Field(
        default=False,
        description="If ``True``, cookies should be supported for cross-origin request",
    )
    allow_methods: List[str] = Field(default=["GET"], description="HTTP Methods allowed for CORS")
    # https://github.com/snok/asgi-correlation-id#cors
    allow_headers: List[str] = Field(
        default=["X-Request-ID", "X-Request-With"],
        description="HTTP headers allowed for CORS",
    )
    expose_headers: List[str] = Field(default=["X-Request-ID"], description="HTTP headers exposed from backend")

    @validator("allow_origins", "allow_methods", "allow_headers", "expose_headers", pre=True)
    def _validate_bootstrap_servers(cls, raw_value: Any):  # noqa: N805
        if not isinstance(raw_value, str):
            return raw_value
        if "[" in raw_value:
            return json.loads(raw_value)
        return [item.strip() for item in raw_value.split(",")]

    class Config:
        extra = "allow"

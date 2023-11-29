# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import textwrap
from typing import Dict, List, Set

from pydantic import BaseModel, Field

from horizon.backend.settings.log import LoggingSettings


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
        HORIZON__SERVER__CORS__ALLOW_ORIGINS=["*"]
        HORIZON__SERVER__CORS__ALLOW_METHODS=["*"]
        HORIZON__SERVER__CORS__ALLOW_HEADERS=["*"]
        HORIZON__SERVER__CORS__EXPOSE_HEADERS=["X-Request-ID"]

    For production environment:

    .. code-block:: bash

        HORIZON__SERVER__CORS__ENABLED=True
        HORIZON__SERVER__CORS__ALLOW_ORIGINS=["production.example.com"]
        HORIZON__SERVER__CORS__ALLOW_METHODS=["GET"]
        HORIZON__SERVER__CORS__ALLOW_HEADERS=["X-Request-ID", "X-Request-With"]
        HORIZON__SERVER__CORS__EXPOSE_HEADERS=["X-Request-ID"]
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

    class Config:
        extra = "allow"


class MonitoringSettings(BaseModel):
    """Monitoring Settings.

    See `starlette-exporter <https://github.com/stephenhillier/starlette_exporter#options>`_ documentation.

    .. note::

        You can pass here any extra option supported by ``starlette-exporter``,
        even if it is not mentioned in documentation.

    Examples
    --------

    .. code-block:: bash

        HORIZON__SERVER__MONITORING__ENABLED=True
        HORIZON__SERVER__MONITORING__SKIP_PATHS=["/some/path"]
        HORIZON__SERVER__MONITORING__SKIP_METHODS=["OPTIONS"]
    """

    enabled: bool = Field(default=True, description="Set to ``True`` to enable middleware")
    labels: Dict[str, str] = Field(
        default_factory=dict,
        description="""Custom labels added to all metrics, e.g. ``{"instance": "production"}``""",
    )
    skip_paths: Set[str] = Field(
        default_factory=set,
        description="Custom paths should be skipped from metrics, like ``/some/endpoint``",
    )
    skip_methods: Set[str] = Field(
        default={"OPTIONS"},
        description="HTTP methods which should be excluded from metrics",
    )
    # These will be new defaults in starlette-exporter 0.18:
    # https://github.com/stephenhillier/starlette_exporter/issues/79
    group_paths: bool = Field(
        default=True,
        description=textwrap.dedent(
            """
            If ``True`` (recommended), add request path to metrics literally as described
            in OpenAPI schema, e.g. ``/namespace/{name}``, without substitution with path real values.

            If ``False``, all real request paths to metrics, e.g. ``/namespace/my-namespace``.
            """,
        ),
    )
    filter_unhandled_paths: bool = Field(
        default=True,
        description=textwrap.dedent(
            """
            If ``True``, add metrics for paths only mentioned in OpenAPI schema.

            If ``False``, add all requested paths to metrics.
            """,
        ),
    )

    class Config:
        extra = "allow"


class RequestIDSettings(BaseModel):
    """X-Request-ID Middleware Settings.

    See `asgi-correlation-id <https://github.com/snok/asgi-correlation-id>`_ documentation.

    Examples
    --------

    .. code-block:: bash

        HORIZON__SERVER__REQUEST_ID__ENABLED=True
        HORIZON__SERVER__REQUEST_ID__UPDATE_REQUEST_HEADER=True
    """

    enabled: bool = Field(default=True, description="Set to ``True`` to enable middleware")
    header_name: str = Field(
        default="X-Request-ID",
        description="Name of response header which is filled up with request ID value",
    )
    update_request_header: bool = Field(
        default=False,
        description=textwrap.dedent(
            """
            If ``False``, bypass header value from request to response as-is.

            If ``True``, always set new value of specific header.
            """,
        ),
    )


class ServerSettings(BaseModel):
    """Backend server settings.

    Examples
    --------

    .. code-block:: bash

        HORIZON__SERVER__DEBUG=True
        HORIZON__SERVER__LOGGING__PRESET=colored
        HORIZON__SERVER__MONITORING__ENABLED=True
        HORIZON__SERVER__CORS__ENABLED=True
        HORIZON__SERVER__REQUEST_ID__ENABLED=True
    """

    debug: bool = Field(
        default=False,
        description=textwrap.dedent(
            """
            :ref:`Enable debug output in responses <backend-configuration-debug>`.
            Do not use this on production!
            """,
        ),
    )
    logging: LoggingSettings = Field(
        default_factory=LoggingSettings,
        description=":ref:`Logging settings <backend-configuration-logging>`",
    )
    cors: CORSSettings = Field(
        default_factory=CORSSettings,
        description=":ref:`CORS settings <backend-configuration-cors>`",
    )
    monitoring: MonitoringSettings = Field(
        default_factory=MonitoringSettings,
        description=":ref:`Monitoring settings <backend-configuration-monitoring>`",
    )
    request_id: RequestIDSettings = Field(
        default_factory=RequestIDSettings,
        description=":ref:`RequestID settings <backend-configuration-debug>`",
    )

# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import textwrap

from pydantic import BaseModel, Field

from horizon.backend.settings.server.application_version import (
    ApplicationVersionSettings,
)
from horizon.backend.settings.server.cors import CORSSettings
from horizon.backend.settings.server.log import LoggingSettings
from horizon.backend.settings.server.monitoring import MonitoringSettings
from horizon.backend.settings.server.openapi import OpenAPISettings
from horizon.backend.settings.server.request_id import RequestIDSettings
from horizon.backend.settings.server.static_files import StaticFilesSettings


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
        HORIZON__SERVER__OPENAPI__ENABLED=True
        HORIZON__SERVER__OPENAPI__SWAGGER__ENABLED=True
        HORIZON__SERVER__OPENAPI__REDOC__ENABLED=True
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
    application_version: ApplicationVersionSettings = Field(
        default_factory=ApplicationVersionSettings,
        description=":ref:`Application version settings <backend-configuration-debug>`",
    )
    static_files: StaticFilesSettings = Field(
        default_factory=StaticFilesSettings,
        description=":ref:`Static files settings <backend-configuration-static-files>`",
    )
    openapi: OpenAPISettings = Field(
        default_factory=OpenAPISettings,
        description=":ref:`OpenAPI.json settings <backend-configuration-openapi>`",
    )

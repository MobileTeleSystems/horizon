# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import FastAPI

from horizon.backend.middlewares.application_version import (
    apply_application_version_middleware,
)
from horizon.backend.middlewares.cors import apply_cors_middleware
from horizon.backend.middlewares.logging import setup_logging
from horizon.backend.middlewares.monitoring import (
    apply_monitoring_metrics_middleware,
    apply_monitoring_stats_middleware,
)
from horizon.backend.middlewares.openapi import apply_openapi_middleware
from horizon.backend.middlewares.request_id import apply_request_id_middleware
from horizon.backend.middlewares.static_files import apply_static_files
from horizon.backend.settings import Settings


def apply_middlewares(
    application: FastAPI,
    settings: Settings,
) -> FastAPI:
    """Add middlewares to the application."""

    if settings.server.logging.setup:
        setup_logging(settings.server.logging.get_log_config_path())

    apply_cors_middleware(application, settings.server.cors)
    apply_monitoring_metrics_middleware(application, settings.server.monitoring)
    apply_monitoring_stats_middleware(application, settings.server.monitoring)
    apply_request_id_middleware(application, settings.server.request_id)
    apply_application_version_middleware(application, settings.server.application_version)
    apply_openapi_middleware(application, settings.server.openapi)
    apply_static_files(application, settings.server.static_files)

    return application

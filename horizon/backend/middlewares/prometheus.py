# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from fastapi import FastAPI

from horizon.backend.settings.server import PrometheusSettings
from horizon.commons.exceptions import SetupError

DEFAULT_SKIP_PATHS = {
    "/monitoring/metrics",
    "/monitoring/ping",
    "/static",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
}


def add_prometheus_middleware(app: FastAPI, settings: PrometheusSettings) -> FastAPI:
    """Add Prometheus middleware to the application."""
    try:
        from starlette_exporter import PrometheusMiddleware, handle_metrics
    except ImportError as e:
        raise SetupError("Please install horizon[prometheus] to expose Prometheus metrics") from e

    skip_paths = DEFAULT_SKIP_PATHS | settings.skip_paths
    app.add_middleware(
        PrometheusMiddleware,
        app_name="horizon",
        skip_paths=skip_paths,
        **settings.dict(exclude={"enabled", "skip_paths"}),
    )
    app.add_route("/monitoring/metrics", handle_metrics)
    return app

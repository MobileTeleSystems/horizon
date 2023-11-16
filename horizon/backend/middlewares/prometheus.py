# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from fastapi import FastAPI
from starlette_exporter import PrometheusMiddleware, handle_metrics

from horizon.backend.settings.server import PrometheusSettings

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
    skip_paths = DEFAULT_SKIP_PATHS | settings.skip_paths
    app.add_middleware(
        PrometheusMiddleware,
        app_name="horizon",
        skip_paths=skip_paths,
        **settings.dict(exclude={"enabled", "skip_paths"}),
    )
    app.add_route("/monitoring/metrics", handle_metrics)
    return app

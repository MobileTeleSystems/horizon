# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter, FastAPI
from starlette.responses import PlainTextResponse
from starlette_exporter import PrometheusMiddleware, handle_metrics

from horizon.backend.settings.server import MonitoringSettings
from horizon.backend.utils.slug import slugify

DEFAULT_SKIP_PATHS = {
    "/monitoring/metrics",
    "/monitoring/ping",
    "/monitoring/stats",
    "/static",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/favicon.ico",
}

router = APIRouter(tags=["Monitoring"], prefix="/monitoring")


router.get(
    "/metrics",
    summary="Get server metrics",
    description="Return server metrics in Prometheus format, using Starlette Exporter",
    response_class=PlainTextResponse,
)(handle_metrics)


def add_monitoring_metrics_middleware(app: FastAPI, settings: MonitoringSettings) -> FastAPI:
    """Add monitoring metrics middleware & endpoint to the application."""
    skip_paths = DEFAULT_SKIP_PATHS | settings.skip_paths
    app.add_middleware(
        PrometheusMiddleware,
        app_name=slugify(app.title),
        skip_paths=skip_paths,
        **settings.dict(exclude={"enabled", "skip_paths"}),
    )
    app.include_router(router)
    return app

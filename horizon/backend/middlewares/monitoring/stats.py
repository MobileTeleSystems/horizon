# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter, Depends, FastAPI, Request
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    CollectorRegistry,
    Gauge,
    generate_latest,
)
from starlette.responses import PlainTextResponse
from typing_extensions import Annotated

from horizon.backend.dependencies.stub import Stub
from horizon.backend.services.uow import UnitOfWork
from horizon.backend.settings import Settings
from horizon.backend.settings.server import MonitoringSettings
from horizon.backend.utils.slug import slugify

router = APIRouter(tags=["Monitoring"], prefix="/monitoring")


@router.get(
    "/stats",
    summary="Get usage stats",
    description="Return the number of users, namespaces and HWMs in database as a Prometheus metrics format",
)
async def stats(
    request: Request,
    unit_of_work: Annotated[UnitOfWork, Depends()],
    settings: Annotated[Settings, Depends(Stub(Settings))],
) -> PlainTextResponse:
    # asyncio.gather cannot be used here https://docs.sqlalchemy.org/en/20/errors.html#error-isce
    user_count_value = await unit_of_work.user.count()
    namespace_count_value = await unit_of_work.namespace.count()
    hwm_count_value = await unit_of_work.hwm.count()

    metrics = [
        (
            "horizon_user_count",
            "Number of users registered in Horizon database",
            user_count_value,
        ),
        (
            "horizon_namespace_count",
            "Number of namespaces created in Horizon database",
            namespace_count_value,
        ),
        (
            "horizon_hwm_count",
            "Number of HWMs created in Horizon database",
            hwm_count_value,
        ),
    ]

    # implementation is the same as used in starlette-exporter:
    # https://github.com/stephenhillier/starlette_exporter/blob/7b011cd/starlette_exporter/__init__.py#L44
    # https://github.com/stephenhillier/starlette_exporter/blob/7b011cd/starlette_exporter/middleware.py#L277
    app_name = slugify(request.app.title)
    registry = CollectorRegistry()
    label_keys = list(settings.server.monitoring.labels.keys())
    label_values = list(settings.server.monitoring.labels.values())

    for name, description, value in metrics:
        Gauge(
            name,
            description,
            registry=registry,
            labelnames=["app_name", *label_keys],
        ).labels(
            app_name,
            *label_values,
        ).set(value)

    headers = {"Content-Type": CONTENT_TYPE_LATEST}
    return PlainTextResponse(generate_latest(registry), headers=headers)


def apply_monitoring_stats_middleware(app: FastAPI, settings: MonitoringSettings) -> FastAPI:
    """Add monitoring stats endpoint to the application."""
    if not settings.enabled:
        return app

    app.include_router(router)
    return app

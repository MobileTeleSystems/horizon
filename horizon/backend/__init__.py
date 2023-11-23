# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Type

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession, async_engine_from_config

import horizon
from horizon.backend.api.handlers import (
    application_exception_handler,
    http_exception_handler,
    service_exception_handler,
    unknown_exception_handler,
    validation_exception_handler,
)
from horizon.backend.api.router import api_router
from horizon.backend.db.factory import create_session_factory
from horizon.backend.middlewares.cors import add_cors_middleware
from horizon.backend.middlewares.logging import setup_logging
from horizon.backend.middlewares.prometheus import add_prometheus_middleware
from horizon.backend.middlewares.request_id import add_request_id_middleware
from horizon.backend.providers.auth.base import AuthProvider
from horizon.backend.settings import Settings
from horizon.commons.exceptions import ApplicationError, ServiceError


def application_factory(settings: Settings) -> FastAPI:
    application = FastAPI(
        title="horizon",
        version=horizon.__version__,
        debug=settings.server.debug,
    )
    application.state.settings = settings
    application.include_router(api_router)

    application.add_exception_handler(ServiceError, service_exception_handler)
    application.add_exception_handler(ApplicationError, application_exception_handler)
    application.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(Exception, unknown_exception_handler)

    engine = async_engine_from_config(settings.database.dict(), prefix="")
    session_factory = create_session_factory(engine)

    application.dependency_overrides.update(
        {
            Settings: lambda: settings,
            AsyncSession: session_factory,  # type: ignore[dict-item]
        },
    )

    # get AuthProvider class from settings, and perform setup
    auth_class: Type[AuthProvider] = settings.auth.provider  # type: ignore[assignment]
    auth_class.setup(application)

    if settings.server.logging.setup:
        setup_logging(settings.server.logging.get_log_config_path())

    if settings.server.cors.enabled:
        add_cors_middleware(application, settings.server.cors)

    if settings.server.prometheus.enabled:
        add_prometheus_middleware(application, settings.server.prometheus)

    if settings.server.request_id.enabled:
        add_request_id_middleware(application, settings.server.request_id)

    return application


def get_application():
    settings = Settings()
    return application_factory(settings=settings)

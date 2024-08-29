# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
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
from horizon.backend.middlewares import apply_middlewares
from horizon.backend.providers.auth.base import AuthProvider
from horizon.backend.settings import Settings
from horizon.commons.exceptions import ApplicationError, ServiceError


def application_factory(settings: Settings) -> FastAPI:
    application = FastAPI(
        title="Horizon",
        description="Horizon is an application that implements simple HWM Store",
        version=horizon.__version__,
        debug=settings.server.debug,
        # will be set up by middlewares
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
    )

    application.state.settings = settings
    application.include_router(api_router)

    application.add_exception_handler(ServiceError, service_exception_handler)  # type: ignore[arg-type]
    application.add_exception_handler(ApplicationError, application_exception_handler)  # type: ignore[arg-type]
    application.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,  # type: ignore[arg-type]
    )
    application.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore[arg-type]
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

    apply_middlewares(application, settings)
    return application


def get_application():
    settings = Settings()
    return application_factory(settings=settings)

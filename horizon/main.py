# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware.cors import CORSMiddleware

from horizon.api.handlers import (
    application_exception_handler,
    http_exception_handler,
    unknown_exception_handler,
    validation_exception_handler,
)
from horizon.api.router import api_router
from horizon.db.factory import create_engine, create_session_factory
from horizon.providers.auth.base import AuthProvider
from horizon.settings import Settings
from horizon_commons.exceptions.base import ApplicationError


def application_factory(settings: Settings) -> FastAPI:
    application = FastAPI(
        title="horizon",
        version="0.1.0",
        debug=settings.server.debug,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router)
    application.add_exception_handler(ApplicationError, application_exception_handler)
    application.add_exception_handler(
        RequestValidationError,
        validation_exception_handler,
    )
    application.add_exception_handler(HTTPException, http_exception_handler)
    application.add_exception_handler(Exception, unknown_exception_handler)

    engine = create_engine(
        connection_uri=settings.database.url,
        **settings.database.engine_args,
    )
    session_factory = create_session_factory(engine)

    application.dependency_overrides.update(
        {
            Settings: lambda: settings,
            AsyncSession: session_factory,  # type: ignore[dict-item]
            AuthProvider: settings.auth.provider_class,
        },
    )
    application.state.settings = settings

    return application


def get_application():
    settings = Settings()
    return application_factory(settings=settings)

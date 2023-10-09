# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import FastAPI, HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import Settings
from app.db.factory import (
    AsyncEngine,
    AsyncSession,
    create_engine,
    create_session_factory,
)
from app.handler import http_exception_handler


def application_factory(settings: Settings) -> FastAPI:
    application = FastAPI(
        title="horizon",
        version="0.1.0",
        debug=settings.DEBUG,
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router)
    application.exception_handler(HTTPException)(http_exception_handler)

    engine = create_engine(connection_uri=settings.DB_URL)
    session_factory = create_session_factory(engine=engine)

    application.dependency_overrides.update(
        {
            Settings: lambda: settings,
            AsyncEngine: lambda: engine,
            AsyncSession: lambda: session_factory,
        },
    )

    return application


def get_application():
    settings = Settings()
    return application_factory(settings=settings)

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from fastapi import FastAPI

from horizon.backend.settings.server import CORSSettings


def add_cors_middleware(app: FastAPI, settings: CORSSettings) -> FastAPI:
    """Add CORS middleware to the application."""
    from starlette.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        **settings.dict(exclude={"enabled"}),
    )
    return app

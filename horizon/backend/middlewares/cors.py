# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from horizon.backend.settings.server import CORSSettings


def apply_cors_middleware(app: FastAPI, settings: CORSSettings) -> FastAPI:
    """Add CORS middleware to the application."""
    if not settings:
        return app

    app.add_middleware(
        CORSMiddleware,
        **settings.dict(exclude={"enabled"}),
    )
    return app

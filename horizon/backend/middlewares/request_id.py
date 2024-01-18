# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from uuid6 import uuid8

from horizon.backend.settings.server import RequestIDSettings


def apply_request_id_middleware(app: FastAPI, settings: RequestIDSettings) -> FastAPI:
    """Add X-Request-ID middleware to the application."""
    if not settings.enabled:
        return app

    app.add_middleware(
        CorrelationIdMiddleware,
        generator=lambda: uuid8().hex,
        **settings.dict(exclude={"enabled"}),
    )
    return app

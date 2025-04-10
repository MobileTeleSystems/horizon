# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from uuid6 import uuid7

from horizon.backend.settings.server import RequestIDSettings


def apply_request_id_middleware(app: FastAPI, settings: RequestIDSettings) -> FastAPI:
    """Add X-Request-ID middleware to the application."""
    if not settings.enabled:
        return app

    app.add_middleware(
        CorrelationIdMiddleware,
        generator=lambda: uuid7().hex,
        validator=None,
        **settings.dict(exclude={"enabled"}),
    )
    return app

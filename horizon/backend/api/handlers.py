# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import http
import logging

from asgi_correlation_id import correlation_id
from fastapi import HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from horizon.backend.settings.server import ServerSettings
from horizon.commons.errors.base import APIErrorSchema, BaseErrorSchema
from horizon.commons.errors.registration import get_response_for_exception
from horizon.commons.exceptions import ApplicationError

logger = logging.getLogger(__name__)


async def http_exception_handler(_request: Request, exc: HTTPException):
    content = BaseErrorSchema(
        code=http.HTTPStatus(exc.status_code).name.lower(),
        message=exc.detail,
        details=None,
    )
    return exception_json_response(
        status=exc.status_code,
        content=content,
        headers=exc.headers,
    )


async def unknown_exception_handler(request: Request, exc: Exception):
    logger.exception("Got unhandled error")

    server: ServerSettings = request.app.state.settings.server

    details = None
    if server.debug:
        details = exc.args

    content = BaseErrorSchema(
        code="unknown",
        message="Got unhandled exception. Please contact support",
        details=details,
    )
    return exception_json_response(
        status=http.HTTPStatus.INTERNAL_SERVER_ERROR.value,
        content=content,
        # https://github.com/snok/asgi-correlation-id#exception-handling
        headers={server.request_id.header_name: correlation_id.get() or ""},
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    response = get_response_for_exception(ValidationError)
    if not response:
        return await unknown_exception_handler(request, exc)

    body = None
    if request.app.state.settings.server.debug:
        try:
            # FormData cannot be serialized to JSON as-is, try to convert it to dict()
            body = dict(exc.body)
        except Exception:
            body = exc.body

    # code and message is set within class implementation
    content = response.schema(  # type: ignore[call-arg]
        details={
            "errors": exc.errors(),
            "body": body,
        },
    )
    return exception_json_response(
        status=response.status,
        content=content,
    )


async def application_exception_handler(request: Request, exc: ApplicationError):
    response = get_response_for_exception(type(exc))
    if not response:
        return await unknown_exception_handler(request, exc)

    # code is set within class implementation
    content = response.schema(  # type: ignore[call-arg]
        message=exc.message,
        details=exc.details,
    )
    return exception_json_response(
        status=response.status,
        content=content,
    )


def exception_json_response(
    status: int,
    content: BaseErrorSchema,
    headers: dict[str, str] | None = None,
) -> Response:
    # Using Response + `model.json()` because JSONResponse + `model.dict()` does not convert Unset() to JSON value "<unset>"
    return Response(
        status_code=status,
        content=APIErrorSchema(error=content).json(exclude_none=True, by_alias=True),
        media_type="application/json",
        headers=headers,
    )

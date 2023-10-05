# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import logging
from typing import Any

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.api.schemas import ErrorSchema
from app.exceptions import HorizonError

logger = logging.getLogger(__name__)


async def http_exception_handler(request: Request, exc: HTTPException):
    return exception_json_response(status_code=exc.status_code, message=exc.detail)


async def horizon_exception_handler(request: Request, exc: HorizonError):
    logger.exception("Got unhandled error")
    return exception_json_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        message="Got unhandled exception. Please contact support.",
    )


def exception_json_response(
    status_code: int,
    message: str,
    code: str | None = None,
    data: Any = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content=ErrorSchema(
            error=True,
            message=message,
            code=code,
            data=data,
        ).dict(),
    )

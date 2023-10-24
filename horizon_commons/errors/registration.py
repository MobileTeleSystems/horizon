# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Any, NamedTuple

from horizon_commons.errors.base import APIErrorSchema, BaseErrorSchema


class APIErrorResponse(NamedTuple):
    status: int
    description: str
    schema: type[BaseErrorSchema]


_responses_by_exception: dict[type[Exception], APIErrorResponse] = {}
_exceptions_by_code: dict[int, APIErrorResponse] = {}


def register_error_response(exception: type[Exception], status: http.HTTPStatus):
    """
    Register mapping between exception, status code and JSON body schema.

    This is used by both routes to show error responses, and by exception handler.
    """

    def wrapper(cls):
        response = APIErrorResponse(status.value, status.phrase, cls)
        _responses_by_exception[exception] = response
        _exceptions_by_code[status.value] = response
        return cls

    return wrapper


def get_response_for_exception(exception_type: type[Exception]) -> APIErrorResponse | None:
    """
    Get mapping between exception type and JSON body schema (for serialization).
    """
    for exception in exception_type.mro():
        if exception in _responses_by_exception:
            return _responses_by_exception[exception]
    return None


def get_error_responses(
    include: set[type[BaseErrorSchema]] | None = None,
    exclude: set[type[BaseErrorSchema]] | None = None,
) -> dict[int | str, dict[str, Any]]:
    """
    Construct FastAPI responses descriptions using specified filters.
    """
    result: dict[int | str, dict[str, Any]] = {}
    for error in _responses_by_exception.values():
        if include and error.schema not in include:
            continue
        if exclude and error.schema in exclude:
            continue

        # https://fastapi.tiangolo.com/advanced/additional-responses/
        result[error.status] = {
            "model": APIErrorSchema[error.schema],  # type: ignore[name-defined]
            "description": error.description,
        }
    return result

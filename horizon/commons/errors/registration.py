# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import http
from typing import Any, NamedTuple, Type

from horizon.commons.errors.base import APIErrorSchema, BaseErrorSchema


class APIErrorResponse(NamedTuple):
    status: int
    description: str
    schema: Type[BaseErrorSchema]


_responses_by_exception: dict[type[Exception], APIErrorResponse] = {}
_responses_by_status_code: dict[int, APIErrorResponse] = {}


def register_error_response(exception: type[Exception], status: http.HTTPStatus):
    """Register mapping between exception, status code and JSON body schema."""

    def wrapper(cls):
        response = APIErrorResponse(status.value, status.phrase, cls)
        _responses_by_exception[exception] = response
        _responses_by_status_code[status.value] = response
        return cls

    return wrapper


def get_response_for_exception(exception_type: type[Exception]) -> APIErrorResponse | None:
    """Get mapping between exception type and JSON body schema (for serialization)."""
    for exception in exception_type.mro():
        if exception in _responses_by_exception:
            return _responses_by_exception[exception]
    return None


def get_response_for_status_code(status_code: int) -> APIErrorResponse | None:
    """Get mapping between status code and JSON body schema (for deserialization)."""
    return _responses_by_status_code.get(status_code, None)


def get_error_responses(
    include: set[type[BaseErrorSchema]] | None = None,
    exclude: set[type[BaseErrorSchema]] | None = None,
) -> dict[int | str, dict[str, Any]]:
    """
    Construct FastAPI responses descriptions using specified filters.
    """
    result: dict[int | str, dict[str, Any]] = {}
    for response in _responses_by_exception.values():
        if include and response.schema not in include:
            continue
        if exclude and response.schema in exclude:
            continue

        # https://fastapi.tiangolo.com/advanced/additional-responses/
        result[response.status] = {
            "model": APIErrorSchema[response.schema],  # type: ignore[name-defined]
            "description": response.description,
        }
    return result

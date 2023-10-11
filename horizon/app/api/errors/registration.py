# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Any, Generic, NamedTuple, TypeVar

from pydantic.generics import GenericModel

from app.api.errors.base import ErrorSchema

ErrorModel = TypeVar("ErrorModel", bound=ErrorSchema)


class APIErrorSchema(GenericModel, Generic[ErrorModel]):
    error: ErrorModel


class APIErrorResponse(NamedTuple):
    status: int
    description: str
    schema: type[ErrorSchema]


_registered_errors: dict[type[Exception], APIErrorResponse] = {}


def register_error_response(exception: type[Exception], status: http.HTTPStatus):
    def wrapper(cls):
        _registered_errors[exception] = APIErrorResponse(status.value, status.phrase, cls)
        return cls

    return wrapper


def get_response_for_exception(exception_type: type[Exception]) -> APIErrorResponse | None:
    for exception in exception_type.mro():
        if exception in _registered_errors:
            return _registered_errors[exception]
    return None


def get_error_responses(
    include: set[type[ErrorSchema]] | None = None,
    exclude: set[type[ErrorSchema]] | None = None,
) -> dict[int | str, dict[str, Any]]:
    """
    Register mapping between exception, status code and JSON body schema.

    This is used by both routes to show error responses, and by exception handler.
    """
    result: dict[int | str, dict[str, Any]] = {}
    for error in _registered_errors.values():
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

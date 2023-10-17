# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Any, Literal

from pydantic import BaseModel

from app.api.errors.base import ErrorSchema
from app.api.errors.registration import register_error_response
from app.exceptions.entity import EntityInvalidError


class InvalidValueDetailsSchema(BaseModel):
    entity_type: str
    field: str
    value: Any


@register_error_response(
    exception=EntityInvalidError,
    status=http.HTTPStatus.EXPECTATION_FAILED,
)
class InvalidValueSchema(ErrorSchema):
    code: Literal["invalid_value"] = "invalid_value"
    details: InvalidValueDetailsSchema

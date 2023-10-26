# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError

from horizon_commons.errors.base import BaseErrorSchema
from horizon_commons.errors.registration import register_error_response


class InvalidRequestBaseErrorSchema(BaseModel):
    loc: list[str] = Field(alias="location")
    msg: str = Field(alias="message")
    type: str = Field(alias="code")

    class Config:
        allow_population_by_field_name = True


class InvalidRequestDetailsSchema(BaseModel):
    errors: list[InvalidRequestBaseErrorSchema]
    body: Any = Field(
        description="Request body. Returned only if server is running in debug mode",
    )


@register_error_response(
    exception=ValidationError,
    status=http.HTTPStatus.UNPROCESSABLE_ENTITY,
)
class InvalidRequestSchema(BaseErrorSchema):
    code: Literal["invalid_request"] = "invalid_request"
    message: Literal["Invalid request"] = "Invalid request"
    details: InvalidRequestDetailsSchema

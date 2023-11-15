# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Any, List

from pydantic import BaseModel, Field, ValidationError
from pydantic import __version__ as pydantic_version
from typing_extensions import Literal

from horizon.commons.errors.base import BaseErrorSchema
from horizon.commons.errors.registration import register_error_response


class InvalidRequestBaseErrorSchema(BaseModel):
    loc: List[str] = Field(alias="location")
    msg: str = Field(alias="message")
    type: str = Field(alias="code")

    if pydantic_version >= "2":
        url: str
        ctx: dict = Field(default_factory=dict, alias="context")
        input: Any = Field(default=None)

    class Config:
        # pydantic v1
        allow_population_by_field_name = True
        # pydantic v2
        populate_by_name = True


@register_error_response(
    exception=ValidationError,
    status=http.HTTPStatus.UNPROCESSABLE_ENTITY,
)
class InvalidRequestSchema(BaseErrorSchema):
    code: Literal["invalid_request"] = "invalid_request"
    message: Literal["Invalid request"] = "Invalid request"
    details: List[InvalidRequestBaseErrorSchema]

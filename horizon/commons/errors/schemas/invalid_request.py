# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Any, List, Union

from pydantic import BaseModel, Field, ValidationError
from pydantic import __version__ as pydantic_version
from typing_extensions import Literal

from horizon.commons.errors.base import BaseErrorSchema
from horizon.commons.errors.registration import register_error_response


class InvalidRequestBaseErrorSchema(BaseModel):
    loc: List[Union[str, int]] = Field(alias="location")
    msg: str = Field(alias="message")
    type: str = Field(alias="code")

    if pydantic_version >= "2":
        ctx: dict = Field(default_factory=dict, alias="context")
        input: Any = Field(default=None)

    class Config:
        if pydantic_version >= "2":
            populate_by_name = True
        else:
            allow_population_by_field_name = True


@register_error_response(
    exception=ValidationError,
    status=http.HTTPStatus.UNPROCESSABLE_ENTITY,
)
class InvalidRequestSchema(BaseErrorSchema):
    code: Literal["invalid_request"] = "invalid_request"
    message: Literal["Invalid request"] = "Invalid request"
    details: List[InvalidRequestBaseErrorSchema]

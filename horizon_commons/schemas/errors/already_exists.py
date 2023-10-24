# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Any, Literal

from pydantic import BaseModel

from horizon_commons.errors.base import BaseErrorSchema
from horizon_commons.errors.registration import register_error_response
from horizon_commons.exceptions.entity import EntityAlreadyExistsError


class AlreadyExistsDetailsSchema(BaseModel):
    entity_type: str
    field: str
    value: Any


@register_error_response(
    exception=EntityAlreadyExistsError,
    status=http.HTTPStatus.CONFLICT,
)
class AlreadyExistsSchema(BaseErrorSchema):
    code: Literal["already_exists"] = "already_exists"
    details: AlreadyExistsDetailsSchema

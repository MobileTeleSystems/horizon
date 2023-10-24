# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import http
from typing import Any, Literal

from pydantic import BaseModel

from horizon_commons.errors.base import BaseErrorSchema
from horizon_commons.errors.registration import register_error_response
from horizon_commons.exceptions.entity import EntityNotFoundError


class NotFoundDetailsSchema(BaseModel):
    entity_type: str
    field: str | None = None
    value: Any | None = None


@register_error_response(
    exception=EntityNotFoundError,
    status=http.HTTPStatus.NOT_FOUND,
)
class NotFoundSchema(BaseErrorSchema):
    code: Literal["not_found"] = "not_found"
    details: NotFoundDetailsSchema

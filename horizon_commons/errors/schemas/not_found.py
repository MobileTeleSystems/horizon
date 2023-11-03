# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

import http
from typing import Any, Optional

from pydantic import BaseModel
from typing_extensions import Literal

from horizon_commons.errors.base import BaseErrorSchema
from horizon_commons.errors.registration import register_error_response
from horizon_commons.exceptions.entity import EntityNotFoundError


class NotFoundDetailsSchema(BaseModel):
    entity_type: str
    field: Optional[str] = None
    value: Optional[Any] = None


@register_error_response(
    exception=EntityNotFoundError,
    status=http.HTTPStatus.NOT_FOUND,
)
class NotFoundSchema(BaseErrorSchema):
    code: Literal["not_found"] = "not_found"
    details: NotFoundDetailsSchema

    def to_exception(self) -> EntityNotFoundError:
        return EntityNotFoundError(
            entity_type=self.details.entity_type,
            field=self.details.field,
            value=self.details.value,
        )

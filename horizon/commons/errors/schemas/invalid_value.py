# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Any

from pydantic import BaseModel
from typing_extensions import Literal

from horizon.commons.errors.base import BaseErrorSchema
from horizon.commons.errors.registration import register_error_response
from horizon.commons.exceptions.entity import EntityInvalidError


class InvalidValueDetailsSchema(BaseModel):
    entity_type: str
    field: str
    value: Any


@register_error_response(
    exception=EntityInvalidError,
    status=http.HTTPStatus.EXPECTATION_FAILED,
)
class InvalidValueSchema(BaseErrorSchema):
    code: Literal["invalid_value"] = "invalid_value"
    details: InvalidValueDetailsSchema

    def to_exception(self) -> EntityInvalidError:
        return EntityInvalidError(
            entity_type=self.details.entity_type,
            field=self.details.field,
            value=self.details.value,
        )

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
import json
from typing import Any, Callable

from pydantic import BaseModel
from pydantic import __version__ as pydantic_version

field_serializer: Callable[..., Any]
try:
    from pydantic import field_serializer
except ImportError:

    def field_serializer(value):  # noqa: WPS440
        return value


from typing_extensions import Literal

from horizon.commons.dto.unset import Unset
from horizon.commons.errors.base import BaseErrorSchema
from horizon.commons.errors.registration import register_error_response
from horizon.commons.exceptions.entity import EntityInvalidError


class InvalidValueDetailsSchema(BaseModel):
    entity_type: str
    field: str
    value: Any

    if pydantic_version >= "2":

        @field_serializer("value")
        def serialize_value(self, value, _info):
            if value is Unset():
                return str(value)
            return json.dumps(value)


@register_error_response(
    exception=EntityInvalidError,
    status=http.HTTPStatus.EXPECTATION_FAILED,
)
class InvalidValueSchema(BaseErrorSchema):
    code: Literal["invalid_value"] = "invalid_value"
    details: InvalidValueDetailsSchema

    def to_exception(self) -> EntityInvalidError:
        value = self.details.value
        if self.details.value == "<unset>":
            value = Unset()

        return EntityInvalidError(
            entity_type=self.details.entity_type,
            field=self.details.field,
            value=value,
        )

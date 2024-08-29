# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Any

from pydantic import BaseModel
from typing_extensions import Literal

from horizon.commons.errors.base import BaseErrorSchema
from horizon.commons.errors.registration import register_error_response
from horizon.commons.exceptions.entity import EntityAlreadyExistsError


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

    def to_exception(self) -> EntityAlreadyExistsError:
        return EntityAlreadyExistsError(
            entity_type=self.details.entity_type,
            field=self.details.field,
            value=self.details.value,
        )

# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http

from pydantic import BaseModel
from typing_extensions import Literal

from horizon.commons.errors.base import BaseErrorSchema
from horizon.commons.errors.registration import register_error_response
from horizon.commons.exceptions import PermissionDeniedError


class PermissionDeniedDetailsSchema(BaseModel):
    required_role: str
    actual_role: str


@register_error_response(
    exception=PermissionDeniedError,
    status=http.HTTPStatus.FORBIDDEN,
)
class PermissionDeniedSchema(BaseErrorSchema):
    code: Literal["permission_denied"] = "permission_denied"
    details: PermissionDeniedDetailsSchema

    def to_exception(self) -> PermissionDeniedError:
        return PermissionDeniedError(
            required_role=self.details.required_role,
            actual_role=self.details.actual_role,
        )

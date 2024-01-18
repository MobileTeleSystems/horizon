# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Any

from typing_extensions import Literal

from horizon.commons.errors.base import BaseErrorSchema
from horizon.commons.errors.registration import register_error_response
from horizon.commons.exceptions.auth import AuthorizationError


@register_error_response(
    exception=AuthorizationError,
    status=http.HTTPStatus.UNAUTHORIZED,
)
class NotAuthorizedSchema(BaseErrorSchema):
    code: Literal["unauthorized"] = "unauthorized"
    details: Any = None

    def to_exception(self) -> AuthorizationError:
        return AuthorizationError(
            message=self.message,
            details=self.details,
        )

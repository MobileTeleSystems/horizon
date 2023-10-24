# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Literal

from horizon_commons.errors.base import BaseErrorSchema
from horizon_commons.errors.registration import register_error_response
from horizon_commons.exceptions.auth import AuthorizationError


@register_error_response(
    exception=AuthorizationError,
    status=http.HTTPStatus.UNAUTHORIZED,
)
class NotAuthorizedSchema(BaseErrorSchema):
    code: Literal["unauthorized"] = "unauthorized"

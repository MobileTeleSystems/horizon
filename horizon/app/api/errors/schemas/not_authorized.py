# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import http
from typing import Literal

from app.api.errors.base import ErrorSchema
from app.api.errors.registration import register_error_response
from app.exceptions.auth import AuthorizationError


@register_error_response(
    exception=AuthorizationError,
    status=http.HTTPStatus.UNAUTHORIZED,
)
class NotAuthorizedSchema(ErrorSchema):
    code: Literal["not_authorized"] = "not_authorized"

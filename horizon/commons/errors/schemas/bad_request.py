# SPDX-FileCopyrightText: 2023-2024 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
import http

from typing_extensions import Literal

from horizon.commons.errors.base import BaseErrorSchema
from horizon.commons.errors.registration import register_error_response
from horizon.commons.exceptions import BadRequestError


@register_error_response(
    exception=BadRequestError,
    status=http.HTTPStatus.BAD_REQUEST,
)
class BadRequestSchema(BaseErrorSchema):
    code: Literal["bad_request"] = "bad_request"

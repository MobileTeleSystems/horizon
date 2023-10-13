# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from app.api.errors.base import ErrorSchema
from app.api.errors.registration import (
    APIErrorResponse,
    get_error_responses,
    get_response_for_exception,
)

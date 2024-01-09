# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from horizon.commons.errors.base import BaseErrorSchema
from horizon.commons.errors.registration import (
    APIErrorResponse,
    get_error_responses,
    get_response_for_exception,
    get_response_for_status_code,
)

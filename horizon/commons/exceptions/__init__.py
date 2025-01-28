# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from horizon.commons.exceptions.auth import AuthorizationError
from horizon.commons.exceptions.bad_request import BadRequestError
from horizon.commons.exceptions.base import ApplicationError
from horizon.commons.exceptions.entity import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
)
from horizon.commons.exceptions.permission import PermissionDeniedError
from horizon.commons.exceptions.service import ServiceError

__all__ = [
    "AuthorizationError",
    "ApplicationError",
    "EntityAlreadyExistsError",
    "PermissionDeniedError",
    "BadRequestError",
    "EntityNotFoundError",
    "ServiceError",
]

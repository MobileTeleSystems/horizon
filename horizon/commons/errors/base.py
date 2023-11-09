# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel


class BaseErrorSchema(BaseModel):
    code: str
    message: str
    details: Any


ErrorModel = TypeVar("ErrorModel", bound=BaseErrorSchema)


class APIErrorSchema(GenericModel, Generic[ErrorModel]):
    error: ErrorModel

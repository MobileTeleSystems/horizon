# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from pydantic import __version__ as pydantic_version
from pydantic.generics import GenericModel

from horizon.commons.dto.unset import Unset


class BaseErrorSchema(BaseModel):
    code: str
    message: str
    details: Any


ErrorModel = TypeVar("ErrorModel", bound=BaseErrorSchema)


class APIErrorSchema(GenericModel, Generic[ErrorModel]):
    error: ErrorModel

    if pydantic_version < "2":

        class Config:
            # https://github.com/pydantic/pydantic/issues/2277
            json_encoders = {
                Unset: str,
            }

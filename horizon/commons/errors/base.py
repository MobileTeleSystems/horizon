# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from pydantic import __version__ as pydantic_version

if pydantic_version >= "2":
    from pydantic import BaseModel as GenericModel  # noqa: WPS474
else:
    from pydantic.generics import GenericModel  # type: ignore[no-redef] # noqa: WPS440

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

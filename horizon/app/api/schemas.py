# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Any, Literal, Optional

from pydantic import BaseModel


class ErrorSchema(BaseModel):
    error: Literal[True]
    message: str
    code: Optional[str] = None
    data: Optional[Any] = None

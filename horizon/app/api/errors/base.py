# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from typing import Any

from pydantic import BaseModel


class ErrorSchema(BaseModel):
    code: str
    message: str
    details: Any

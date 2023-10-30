# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

from pydantic import BaseModel


class AuthTokenResponseV1(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    refresh_token: str

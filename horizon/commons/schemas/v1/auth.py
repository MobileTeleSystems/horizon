# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pydantic import BaseModel


class AuthTokenResponseV1(BaseModel):
    access_token: str
    token_type: str
    expires_at: float

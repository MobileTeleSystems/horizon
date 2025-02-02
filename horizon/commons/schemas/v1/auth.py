# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pydantic import BaseModel


class AuthTokenResponseV1(BaseModel):
    """Authorization response."""

    access_token: str
    token_type: str
    expires_at: float

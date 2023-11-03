# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from typing import Optional

from pydantic import BaseModel


class JWTSettings(BaseModel):
    # Key is optional because some AuthProviders does not require it.
    # If some provider depends on key presence, it should raise an exception
    secret_key: Optional[str] = None
    security_algorithm: str = "HS256"
    token_expired_seconds: int = 10 * 60 * 60

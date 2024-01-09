# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

from pydantic import BaseModel
from typing_extensions import Literal


class PingResponse(BaseModel):
    """Ping result"""

    status: Literal["ok"] = "ok"

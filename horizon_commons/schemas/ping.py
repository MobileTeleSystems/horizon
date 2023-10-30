# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

from pydantic import BaseModel


class PingResponse(BaseModel):
    """Ping result"""

    status: Literal["ok"] = "ok"

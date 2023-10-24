# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Monitoring"], prefix="/monitoring")


class PingSchema(BaseModel):
    status: Literal["ok"] = "ok"


@router.get("/ping")
async def ping() -> PingSchema:
    return PingSchema()

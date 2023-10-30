# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter

from horizon_commons.schemas import PingResponse

router = APIRouter(tags=["Monitoring"], prefix="/monitoring")


@router.get("/ping")
async def ping() -> PingResponse:
    return PingResponse()

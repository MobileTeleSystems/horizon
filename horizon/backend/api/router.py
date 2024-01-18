# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter

from horizon.backend.api.monitoring import router as monitoring_router
from horizon.backend.api.v1.router import router as v1_router

api_router = APIRouter()
api_router.include_router(monitoring_router)
api_router.include_router(v1_router)

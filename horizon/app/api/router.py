# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter

from app.api import monitoring, v1

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(v1.router)

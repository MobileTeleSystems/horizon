# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from fastapi import APIRouter

from app.api import monitoring

api_router = APIRouter()
api_router.include_router(monitoring.router)

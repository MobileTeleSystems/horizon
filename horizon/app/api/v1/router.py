# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter

from app.api.v1.auth.router import router as auth_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)

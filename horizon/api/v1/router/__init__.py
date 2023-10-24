# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter

from horizon.api.v1.router.auth import router as auth_router
from horizon.api.v1.router.namespaces import router as namespaces_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(namespaces_router)

# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from fastapi import APIRouter

from horizon.backend.api.v1.router.auth import router as auth_router
from horizon.backend.api.v1.router.hwm import router as hwm_router
from horizon.backend.api.v1.router.hwm_history import router as hwm_history_router
from horizon.backend.api.v1.router.namespace_history import (
    router as namespace_history_router,
)
from horizon.backend.api.v1.router.namespaces import router as namespaces_router
from horizon.backend.api.v1.router.permission import router as permission_router
from horizon.backend.api.v1.router.users import router as users_router

router = APIRouter(prefix="/v1")
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(namespaces_router)
router.include_router(hwm_router)
router.include_router(hwm_history_router)
router.include_router(namespace_history_router)
router.include_router(permission_router)

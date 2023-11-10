# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from fastapi import FastAPI

from horizon.backend.db.models import User


class AuthProvider(ABC):
    @classmethod
    @abstractmethod
    def setup(cls, app: FastAPI) -> FastAPI:
        ...

    @abstractmethod
    async def get_current_user(self, access_token: str) -> User:
        ...

    @abstractmethod
    async def get_token(
        self,
        grant_type: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> Dict[str, Any]:
        ...

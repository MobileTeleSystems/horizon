# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from abc import ABC, abstractmethod

from fastapi import Request

from horizon.db.models.user import User


class AuthProvider(ABC):
    @abstractmethod
    async def get_current_user(self, request: Request) -> User:
        ...

    @abstractmethod
    async def get_tokens(
        self,
        grant_type: str,
        username: str | None = None,
        password: str | None = None,
        scopes: list[str] | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> tuple[str, str]:
        ...

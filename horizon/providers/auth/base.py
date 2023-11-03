# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from horizon.db.models.user import User


class AuthProvider(ABC):
    @abstractmethod
    async def get_current_user(self, access_token: str) -> User:
        ...

    @abstractmethod
    async def get_tokens(
        self,
        grant_type: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        scopes: Optional[List[str]] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> Tuple[str, str]:
        ...

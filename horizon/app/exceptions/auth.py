# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0


from app.exceptions.base import ApplicationError


class AuthorizationError(ApplicationError):
    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self) -> str:
        return self._message

    @property
    def details(self) -> None:
        pass

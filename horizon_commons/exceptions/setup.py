# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from horizon_commons.exceptions.base import ApplicationError


class SetupError(ApplicationError):
    def __init__(self, message: str):
        self._message = message

    @property
    def message(self) -> str:
        return self._message

    @property
    def details(self) -> None:
        pass

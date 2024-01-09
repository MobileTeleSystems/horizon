# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0


from horizon.commons.exceptions.base import ApplicationError


class ServiceError(ApplicationError):
    """Service used by application have not responded properly.

    Examples
    --------

    .. code-block:: python

        raise ServiceError("Some server response is invalid")
    """

    def __init__(self, message: str) -> None:
        self._message = message

    @property
    def message(self) -> str:
        return self._message

    @property
    def details(self) -> None:
        pass

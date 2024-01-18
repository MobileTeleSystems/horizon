# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field

try:
    from pydantic import ImportString
except ImportError:
    from pydantic import PyObject as ImportString  # type: ignore[no-redef] # noqa: WPS440

from horizon.backend.providers.auth.dummy import DummyAuthProvider


class AuthSettings(BaseModel):
    """Authorization-related settings.

    Here you can set auth provider class along with its options.

    Examples
    --------

    .. code-block:: bash

        # set settings.auth.provider = horizon.backend.providers.auth.dummy.DummyAuthProvider
        HORIZON__AUTH__PROVIDER=horizon.backend.providers.auth.dummy.DummyAuthProvider

        # pass access_key.secret_key = "secret" to DummyAuthProviderSettings
        HORIZON__AUTH__ACCESS_KEY__SECRET_KEY=secret
    """

    provider: ImportString = Field(  # type: ignore[assignment]
        default=DummyAuthProvider,
        description="Full name of auth provider class",
    )

    class Config:
        extra = "allow"

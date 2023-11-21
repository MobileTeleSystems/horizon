# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel, Field

from horizon.backend.settings.auth.jwt import JWTSettings


class DummyAuthProviderSettings(BaseModel):
    """Settings for DummyAuthProvider.

    Examples
    --------

    .. code-block:: bash

        HORIZON__AUTH__PROVIDER=horizon.backend.providers.auth.dummy.DummyAuthProvider
        HORIZON__AUTH__ACCESS_KEY__SECRET_KEY=secret
    """

    access_token: JWTSettings = Field(description="Access-token related settings")

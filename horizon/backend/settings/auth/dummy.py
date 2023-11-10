# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from pydantic import BaseModel

from horizon.backend.settings.auth.jwt import JWTSettings


class DummyAuthProviderSettings(BaseModel):
    access_token: JWTSettings

# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field, PyObject

from horizon.backend.settings.auth.jwt import JWTSettings


class AuthSettings(BaseModel):
    provider_class: PyObject = "horizon.backend.providers.auth.dummy.DummyAuthProvider"  # type: ignore[assignment]
    access_token: JWTSettings

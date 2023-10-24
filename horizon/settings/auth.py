# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, PyObject


class AuthSettings(BaseModel):
    provider_class: PyObject = "horizon.providers.auth.dummy.DummyAuthProvider"  # type: ignore[assignment]
    schema_class: PyObject = "fastapi.security.OAuth2PasswordBearer"  # type: ignore[assignment]
    schema_args: dict = {"tokenUrl": "v1/auth/token"}

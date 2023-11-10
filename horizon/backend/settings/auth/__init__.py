# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field, PyObject


class AuthProviderSettings(BaseModel):
    klass: PyObject = Field(default="horizon.backend.providers.auth.dummy.DummyAuthProvider", alias="class")  # type: ignore[assignment]

    class Config:
        extra = "allow"

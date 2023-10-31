# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, PyObject


class AuthSettings(BaseModel):
    provider_class: PyObject = "horizon.providers.auth.dummy.DummyAuthProvider"  # type: ignore[assignment]

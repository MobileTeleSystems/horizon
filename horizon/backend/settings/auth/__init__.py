# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel, Field

try:
    from pydantic import ImportString
except ImportError:
    from pydantic import PyObject as ImportString  # type: ignore[no-redef] # noqa: WPS440

from horizon.backend.providers.auth.dummy import DummyAuthProvider


class AuthSettings(BaseModel):
    provider: ImportString = Field(  # type: ignore[assignment]
        default=DummyAuthProvider,
        description="Full name of auth provider class",
    )

    class Config:
        extra = "allow"

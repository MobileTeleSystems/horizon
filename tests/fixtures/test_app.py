# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import pytest
from fastapi import FastAPI

from horizon.backend import application_factory
from horizon.backend.settings import Settings


@pytest.mark.backend
@pytest.fixture(scope="session")
def test_app(settings: Settings) -> FastAPI:
    return application_factory(settings=settings)

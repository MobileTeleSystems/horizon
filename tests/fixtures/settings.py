# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import pytest

from horizon.backend.settings import Settings


@pytest.fixture(scope="session", params=[{}])
def settings(request: pytest.FixtureRequest) -> Settings:
    return Settings.parse_obj(request.param)

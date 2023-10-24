# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import pytest

from horizon.settings import Settings


@pytest.fixture(scope="session", params=[{}])
def settings(request: pytest.FixtureRequest):
    return Settings(**request.param)

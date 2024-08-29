# SPDX-FileCopyrightText: 2023 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import os

import pytest


@pytest.fixture(scope="session")
def external_app_url() -> str:
    return os.environ["HORIZON_TEST_SERVER_URL"]

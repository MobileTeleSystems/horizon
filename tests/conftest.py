# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
pytest_plugins = [
    "tests.fixtures.event_loop",
    "tests.fixtures.settings",
    "tests.fixtures.test_app",
    "tests.fixtures.test_client",
    "tests.fixtures.external_app",
    "tests.fixtures.sync_client",
    "tests.fixtures.alembic",
    "tests.fixtures.async_engine",
    "tests.fixtures.async_session",
    "tests.fixtures.jwt",
    "tests.factories.user",
    "tests.factories.credentials_cache",
    "tests.factories.namespace",
    "tests.factories.namespace_history",
    "tests.factories.hwm",
    "tests.factories.hwm_history",
    "tests.factories.permissions",
]

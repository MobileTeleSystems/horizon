pytest_plugins = [
    "tests.fixtures.event_loop",
    "tests.fixtures.settings",
    "tests.fixtures.client",
    "tests.fixtures.alembic",
    "tests.fixtures.engine",
    "tests.fixtures.session",
    "tests.fixtures.jwt",
    "tests.factories.user",
    "tests.factories.namespace",
    "tests.factories.hwm",
]

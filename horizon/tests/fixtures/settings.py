import pytest

from app.settings import Settings


@pytest.fixture(scope="session", params=[{}])
def settings(request: pytest.FixtureRequest):
    return Settings(**request.param)

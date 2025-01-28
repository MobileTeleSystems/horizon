import pytest

from horizon.backend.settings import Settings


@pytest.fixture(scope="session", params=[{}])
def settings(request: pytest.FixtureRequest) -> Settings:
    return Settings.parse_obj(request.param)

import pytest

from app.config import Settings


@pytest.fixture(scope="session")
def settings():
    return Settings()

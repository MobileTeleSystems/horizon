from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from horizon.backend import application_factory

if TYPE_CHECKING:
    from fastapi import FastAPI

    from horizon.backend.settings import Settings


@pytest.fixture(scope="session")
def test_app(settings: Settings) -> FastAPI:
    return application_factory(settings=settings)

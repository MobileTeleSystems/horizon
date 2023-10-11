import pytest

from app.db.models.user import User
from app.settings.jwt import JWTSettings
from app.utils.jwt import sign_jwt


@pytest.fixture
def fake_access_token(new_user: User, jwt_settings: JWTSettings):
    return sign_jwt(new_user.id, jwt_settings)


@pytest.fixture
def real_access_token(user: User, jwt_settings: JWTSettings):
    return sign_jwt(user.id, jwt_settings)

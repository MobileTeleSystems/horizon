from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserFactory(SQLAlchemyFactory[User]):
    __model__ = User

    is_active = True
    is_deleted = False


@pytest_asyncio.fixture(params=[{}])
async def new_user(request: pytest.FixtureRequest, session: AsyncSession) -> AsyncGenerator[User, None]:
    params = request.param
    user = UserFactory.build(**params)
    yield user

    query = delete(User).where(User.username == user.username)
    await session.execute(query)
    await session.commit()


@pytest_asyncio.fixture(params=[{}])
async def user(request: pytest.FixtureRequest, session: AsyncSession) -> AsyncGenerator[User, None]:
    UserFactory.__async_session__ = session
    params = request.param
    user = await UserFactory.create_async(**params)
    yield user

    await session.delete(user)
    await session.commit()

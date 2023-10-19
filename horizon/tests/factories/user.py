from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from polyfactory import Ignore
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User


class UserFactory(SQLAlchemyFactory[User]):
    __model__ = User

    is_active = True
    is_deleted = False
    created_at = Ignore()
    updated_at = Ignore()


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

    # remove current object from Session. this is required to compare object against new state fetched
    # from database, and also to remove it from cache
    user_id = user.id
    session.expunge(user)
    yield user

    query = delete(User).where(User.id == user_id)
    await session.execute(query)
    await session.commit()

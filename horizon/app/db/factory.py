# SPDX-FileCopyrightText: 2023 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0

from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


def create_engine(connection_uri: str, **engine_kwargs: Any) -> AsyncEngine:
    return create_async_engine(url=connection_uri, **engine_kwargs)


def sessionmaker(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


def create_session_factory(engine: AsyncEngine):
    Session = sessionmaker(engine)  # noqa: N806

    async def wrapper() -> AsyncGenerator[AsyncSession, None]:
        async with Session.begin() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    return wrapper

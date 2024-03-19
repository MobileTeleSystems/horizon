#!/bin/env python3

# SPDX-FileCopyrightText: 2023-2024 MTS (Mobile Telesystems)
# SPDX-License-Identifier: Apache-2.0
import argparse
import asyncio
from typing import List

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.future import select

from horizon.backend.db.models import User
from horizon.backend.settings import Settings

engine = create_async_engine(Settings().database.url)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)


async def add_admins(session: AsyncSession, usernames: List[str]):
    for username in usernames:
        result = await session.execute(select(User).filter_by(username=username))
        user = result.scalars().first()
        if user:
            user.is_admin = True
        else:
            user = User(username=username, is_admin=True)
            session.add(user)
    await session.commit()


async def remove_admins(session: AsyncSession, usernames: List[str]):
    for username in usernames:
        result = await session.execute(select(User).filter_by(username=username))
        user = result.scalars().first()
        if user:
            user.is_admin = False
    await session.commit()


async def main():
    parser = argparse.ArgumentParser(description="Manage admin users.")
    parser.add_argument("--add", nargs="+", help="Usernames to add as admins")
    parser.add_argument("--remove", nargs="+", help="Usernames to remove from admins")

    args = parser.parse_args()

    async with SessionLocal() as session:
        if args.add:
            await add_admins(session, args.add)
        if args.remove:
            await remove_admins(session, args.remove)


if __name__ == "__main__":
    asyncio.run(main())

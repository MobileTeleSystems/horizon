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


async def list_admins(session: AsyncSession):
    result = await session.execute(select(User).filter_by(is_admin=True))
    admins = result.scalars().all()
    for admin in admins:
        print(admin.username)


def create_parser():
    parser = argparse.ArgumentParser(description="Manage admin users.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    parser_add = subparsers.add_parser("add", help="Add admin privileges to users")
    parser_add.add_argument("usernames", nargs="+", help="Usernames to add as admins")
    parser_add.set_defaults(func=add_admins)

    parser_remove = subparsers.add_parser("remove", help="Remove admin privileges from users")
    parser_remove.add_argument("usernames", nargs="+", help="Usernames to remove from admins")
    parser_remove.set_defaults(func=remove_admins)

    parser_list = subparsers.add_parser("list", help="List all admins")
    parser_list.set_defaults(func=list_admins)

    return parser


async def main(args: argparse.Namespace, session: AsyncSession):
    async with session:
        if args.command == "list":
            # 'list' command does not take additional arguments
            await args.func(session)
        else:
            await args.func(session, args.usernames)


if __name__ == "__main__":
    settings = Settings()
    engine = create_async_engine(settings.database.url)
    SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    parser = create_parser()
    args = parser.parse_args()
    session = SessionLocal()
    asyncio.run(main(args, session))

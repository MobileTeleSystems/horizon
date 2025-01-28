#!/bin/env python3

# SPDX-FileCopyrightText: 2023-2025 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import argparse
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.future import select

from horizon.backend.db.models import User
from horizon.backend.middlewares import setup_logging
from horizon.backend.settings import Settings


async def add_admins(session: AsyncSession, usernames: list[str]) -> None:
    logging.info("Adding SUPERADMIN users:")
    result = await session.execute(select(User).where(User.username.in_(usernames)).order_by(User.username))
    users = result.scalars().all()

    not_found = set(usernames)
    for user in users:
        user.is_admin = True
        logging.info("    %r", user.username)
        not_found.discard(user.username)

    if not_found:
        for username in not_found:
            session.add(User(username=username, is_admin=True))
            logging.info("    %r (new user)", username)

    await session.commit()
    logging.info("Done.")


async def remove_admins(session: AsyncSession, usernames: list[str]) -> None:
    logging.info("Removing SUPERADMIN users:")
    result = await session.execute(select(User).where(User.username.in_(usernames)).order_by(User.username))
    users = result.scalars().all()

    not_found = set(usernames)
    for user in users:
        logging.info("    %r", user.username)
        user.is_admin = False
        not_found.discard(user.username)

    if not_found:
        logging.info("Not found:")
        for username in not_found:
            logging.info("    %r", username)

    await session.commit()
    logging.info("Done.")


async def list_admins(session: AsyncSession) -> None:
    result = await session.execute(select(User).filter_by(is_admin=True).order_by(User.username))
    admins = result.scalars().all()
    logging.info("Listing users with SUPERADMIN role:")
    for admin in admins:
        logging.info("    %r", admin.username)
    logging.info("Done.")


def create_parser() -> argparse.ArgumentParser:
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


async def main(args: argparse.Namespace, session: AsyncSession) -> None:
    async with session:
        if args.command == "list":
            # 'list' command does not take additional arguments
            await args.func(session)
        else:
            await args.func(session, args.usernames)


if __name__ == "__main__":
    settings = Settings()
    if settings.server.logging.setup:
        setup_logging(settings.server.logging.get_log_config_path())

    engine = create_async_engine(settings.database.url)
    SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)
    parser = create_parser()
    args = parser.parse_args()
    session = SessionLocal()
    asyncio.run(main(args, session))

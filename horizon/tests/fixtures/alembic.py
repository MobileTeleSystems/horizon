from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import pytest_asyncio
from alembic.config import Config as AlembicConfig
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.db.base import Base

if TYPE_CHECKING:
    from sqlalchemy import Connection, MetaData

    from app.config import Settings

PROJECT_PATH = Path(__file__).parent.parent.parent.resolve()


@pytest.fixture(scope="session")
def alembic_config(settings: Settings) -> AlembicConfig:
    alembic_cfg = AlembicConfig(PROJECT_PATH / "alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", settings.DB_URL)
    alembic_cfg.set_main_option(
        "script_location",
        os.fspath(PROJECT_PATH / "app/db/migrations"),
    )
    return alembic_cfg


@pytest_asyncio.fixture(scope="session")
async def run_migrations(alembic_config: AlembicConfig):
    try:
        await run_async_migrations(alembic_config, Base.metadata, "-1", "down")
    except Exception:  # noqa: S110
        pass
    await run_async_migrations(alembic_config, Base.metadata, "head")


def do_run_migrations(
    connection: Connection,
    target_metadata: MetaData,
    context: EnvironmentContext,
) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations(
    config: AlembicConfig,
    target_metadata: MetaData,
    revision: str,
    action="up",
) -> None:
    script = ScriptDirectory.from_config(config)

    def upgrade(rev, context):  # noqa: WPS430
        return script._upgrade_revs(revision, rev)  # noqa: WPS437

    def downgrade(rev, context):  # noqa: WPS430
        return script._downgrade_revs(revision, rev)  # noqa: WPS437

    with EnvironmentContext(
        config,
        script=script,
        fn=upgrade if action == "up" else downgrade,
        as_sql=False,
        starting_rev=None,
        destination_rev=revision,
    ) as context:
        connectable = async_engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        async with connectable.connect() as connection:
            await connection.run_sync(
                do_run_migrations,
                target_metadata=target_metadata,
                context=context,
            )

        await connectable.dispose()

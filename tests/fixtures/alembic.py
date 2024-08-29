# SPDX-FileCopyrightText: 2023 MTS PJSC
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import os
import secrets
from contextlib import suppress
from pathlib import Path
from typing import TYPE_CHECKING, Generator
from urllib.parse import urlparse

import pytest
from alembic.config import Config as AlembicConfig
from alembic.runtime.environment import EnvironmentContext
from alembic.script import ScriptDirectory
from sqlalchemy import engine_from_config, pool
from sqlalchemy_utils.functions import create_database, database_exists, drop_database

from horizon.backend.db.models import Base

if TYPE_CHECKING:
    from sqlalchemy import MetaData

    from horizon.backend.settings import Settings

PROJECT_PATH = Path(__file__).parent.parent.parent.joinpath("horizon/backend").resolve()


@pytest.fixture
def empty_db_url(settings: Settings) -> Generator[str, None, None]:
    """Create new test DB to run migrations"""
    new_db = secrets.token_hex(8)
    original_url = urlparse(settings.database.url)

    # updating original url with temp database name, and use it only for running migrations
    # sqlalchemy-utils does not support asyncio, so using sync action instead
    new_url = original_url._replace(scheme="postgresql+psycopg2", path=new_db).geturl()  # noqa: WPS437

    if not database_exists(new_url):
        create_database(new_url)

    yield new_url

    drop_database(new_url)


@pytest.fixture
def alembic_config(empty_db_url: str) -> AlembicConfig:
    alembic_cfg = AlembicConfig(PROJECT_PATH / "db/migrations/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", empty_db_url)
    alembic_cfg.set_main_option(
        "script_location",
        os.fspath(PROJECT_PATH / "db/migrations"),
    )
    return alembic_cfg


@pytest.fixture
def run_migrations(alembic_config: AlembicConfig) -> None:
    with suppress(Exception):
        do_run_migrations(alembic_config, Base.metadata, "-1", "down")
    do_run_migrations(alembic_config, Base.metadata, "head")


def do_run_migrations(
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
        engine = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

        with engine.connect() as connection:
            context.configure(connection=connection, target_metadata=target_metadata)

            with context.begin_transaction():
                context.run_migrations()

        engine.dispose()

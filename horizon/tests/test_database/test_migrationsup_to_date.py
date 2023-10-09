import pytest
from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import Connection, MetaData
from sqlalchemy.ext.asyncio import AsyncEngine

from app.db.base import Base


def get_diff_db_metadata(connection: Connection, metadata: MetaData):
    migration_ctx = MigrationContext.configure(connection)
    return compare_metadata(context=migration_ctx, metadata=metadata)


@pytest.mark.asyncio
async def test_migrations_up_to_date(engine: AsyncEngine):
    async with engine.connect() as connection:
        diff = await connection.run_sync(
            get_diff_db_metadata,
            metadata=(Base.metadata,),
        )
    assert not diff

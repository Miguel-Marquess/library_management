from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

from library_management.models.db_models import registry_table
from library_management.settings import Settings

settings = Settings()

engine = create_async_engine(settings.DATABASE_URL)

registry_table.metadata.create_all


async def get_session():  # pragma: no cover
    async with AsyncSession(engine, expire_on_commit=False) as ss:
        yield ss

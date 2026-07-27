import os

from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from file_catalog.config import Config
from file_catalog.models import Base
from file_catalog.services import FileService


async def init_db(container: AsyncContainer) -> None:
    engine = await container.get(AsyncEngine)
    sessionmaker = await container.get(async_sessionmaker[AsyncSession])

    config = container.get_sync(Config)
    os.makedirs(config.FILES_DIR, exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with sessionmaker() as session:
        # Do not pass candidate_service, because it isn't needed
        # in .create_or_update_files()
        file_service = FileService(
            session,
            candidate_service=None,  # type: ignore[arg-type]
            config=config,
        )
        await file_service.create_or_update_files()

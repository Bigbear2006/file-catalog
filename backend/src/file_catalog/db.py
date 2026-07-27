import os
import random
import string
import uuid
from pathlib import Path

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
        await create_or_update_files(session, config)


def generate_files(count: int, *, file_length: int, files_dir: Path) -> None:
    for _ in range(count):
        with open(files_dir / f'{uuid.uuid4()}.txt', 'w') as file:
            content = ''.join(
                [random.choice(string.digits) for _ in range(file_length)]
            )
            file.write(content)


async def create_or_update_files(
    session: AsyncSession, config: Config
) -> None:
    # Do not pass candidate_service, because it isn't needed
    # in .create_or_update_files()
    file_service = FileService(
        session,
        candidate_service=None,  # type: ignore[arg-type]
        config=config,
    )
    await file_service.create_or_update_files()

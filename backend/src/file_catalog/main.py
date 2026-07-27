import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)
from starlette.middleware.base import BaseHTTPMiddleware

from file_catalog.api import api_router
from file_catalog.api.exceptions import setup_exception_handler
from file_catalog.config import Config
from file_catalog.di.container import container
from file_catalog.logging import configure_logging, logger
from file_catalog.middleware import cors_middleware
from file_catalog.models import Base
from file_catalog.services import FileService


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
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

    yield

    await _app.state.dishka_container.close()


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title='File Catalog API',
        version='0.1.0',
        docs_url='/api/docs',
        openapi_url='/api/openapi.json',
        lifespan=lifespan,
    )
    app.include_router(api_router)
    app.add_middleware(BaseHTTPMiddleware, dispatch=cors_middleware)
    setup_exception_handler(app)
    setup_dishka(container, app)
    return app


if __name__ == '__main__':
    logger.info('Application started')
    uvicorn.run(
        app=create_app(),
        host='0.0.0.0',
        port=8000,
    )

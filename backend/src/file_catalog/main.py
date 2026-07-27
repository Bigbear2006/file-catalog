from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware

from file_catalog.api import api_router
from file_catalog.api.exceptions import setup_exception_handler
from file_catalog.db import init_db
from file_catalog.di.container import container
from file_catalog.logging import configure_logging, logger
from file_catalog.middleware import cors_middleware


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    await init_db(container)
    yield
    await _app.state.dishka_container.close()


def create_app(_container: AsyncContainer) -> FastAPI:
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
    setup_dishka(_container, app)
    return app


if __name__ == '__main__':
    logger.info('Application started')
    uvicorn.run(
        app=create_app(container),
        host='0.0.0.0',
        port=8000,
    )

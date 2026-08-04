from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from dishka import AsyncContainer
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from file_catalog.api import api_router
from file_catalog.api.exceptions import setup_exception_handler
from file_catalog.di.container import container
from file_catalog.logging import configure_logging, logger
from file_catalog.services.file import load_files

ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://localhost:3000',
]


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    await load_files(container)
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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_methods=['GET', 'POST', 'OPTIONS', 'PUT', 'PATCH', 'DELETE'],
        allow_headers=['Content-Type'],
        expose_headers=['Retry-After', 'Content-Disposition'],
    )
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

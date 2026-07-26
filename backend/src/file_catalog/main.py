from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI, Request, Response
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession
from starlette.middleware.base import BaseHTTPMiddleware

from file_catalog.api import api_router
from file_catalog.api.exceptions import setup_exception_handler
from file_catalog.config import Config
from file_catalog.di.container import container
from file_catalog.models import Base
from file_catalog.services import FileService


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    engine = await container.get(AsyncEngine)
    sessionmaker = await container.get(async_sessionmaker[AsyncSession])
    config = container.get_sync(Config)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with sessionmaker() as session:
        # Do not pass candidate_service, because it isn't needed
        # in .create_or_update_files()
        file_service = FileService(session, candidate_service=None, config=config)  # type: ignore[arg-type]
        await file_service.create_or_update_files()

    yield

    app.state.dishka_container.close()


async def cors_middleware(request: Request, call_next: Any) -> Response:
    if request.method == 'OPTIONS':
        rsp = Response()
    else:
        rsp = await call_next(request)

    origin = request.headers.get('origin')
    if origin and 'localhost:5173' in origin:
        rsp.headers['Access-Control-Allow-Origin'] = origin
        rsp.headers['Access-Control-Allow-Credentials'] = 'true'
        rsp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        rsp.headers['Access-Control-Allow-Methods'] = (
            'GET,POST,OPTIONS,PUT,PATCH,DELETE'
        )
    return rsp


def create_app() -> FastAPI:
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
    uvicorn.run(
        app=create_app(),
        host='0.0.0.0',
        port=8000,
    )

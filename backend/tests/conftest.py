import os
import shutil
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from json import JSONDecodeError
from typing import Any

import httpx
import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from file_catalog.config import Config
from file_catalog.main import create_app
from file_catalog.services.file import generate_files, load_files
from httpx import URL, ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from tests.di.container import test_container


@pytest.fixture(scope='session')
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope='session', autouse=True)
async def setup_db() -> AsyncIterator[None]:
    config = test_container.get_sync(Config)
    os.makedirs(config.FILES_DIR, exist_ok=True)
    generate_files(5, file_length=500, files_dir=config.FILES_DIR)

    app_config = test_container.get_sync(Config)
    alembic_config = AlembicConfig('alembic.ini')
    section = alembic_config.config_ini_section
    alembic_config.set_section_option(
        section,
        'DATABASE_URL',
        app_config.database_url,
    )

    engine = await test_container.get(AsyncEngine)
    async with engine.connect() as conn:
        await conn.run_sync(lambda _: command.upgrade(alembic_config, 'head'))

    await load_files(test_container)
    try:
        yield
    finally:
        async with engine.connect() as conn:
            await conn.run_sync(
                lambda _: command.downgrade(alembic_config, 'base')
            )
        shutil.rmtree(config.FILES_DIR)


class CustomAsyncClient(AsyncClient):
    async def request(
        self,
        method: str,
        url: URL | str,
        **kwargs: Any,
    ) -> httpx.Response:
        rsp = await super().request(method, url, **kwargs)

        try:
            data = rsp.json()
        except (JSONDecodeError, UnicodeDecodeError):
            data = ''

        print(f'{rsp.status_code} {method} {url}\n{data}\n')
        return rsp


@asynccontextmanager
async def create_test_client() -> AsyncIterator[CustomAsyncClient]:
    app = create_app(test_container)
    async with CustomAsyncClient(
        transport=ASGITransport(app=app),
        base_url='http://localhost/api',
    ) as client:
        yield client


@pytest.fixture(scope='function')
async def client() -> AsyncIterator[CustomAsyncClient]:
    async with create_test_client() as client:
        yield client


@pytest.fixture(scope='session')
async def candidate_ip() -> str:
    return '127.0.0.1'


@pytest.fixture(scope='session')
async def x_candidate_id() -> str:
    return 'test-candidate'


@pytest.fixture(scope='session')
async def candidate_headers(x_candidate_id: str) -> dict[str, str]:
    return {'X-Candidate-Id': x_candidate_id}


@pytest.fixture(scope='session')
async def admin_headers() -> dict[str, str]:
    config = test_container.get_sync(Config)
    return {'X-Admin-Token': config.ADMIN_TOKEN}

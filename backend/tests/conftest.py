from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from json import JSONDecodeError
from typing import Any

import httpx
import pytest
from file_catalog.config import Config
from file_catalog.db import init_db
from file_catalog.main import create_app
from file_catalog.models import Base
from httpx import URL, ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from tests.di.container import test_container


@pytest.fixture(scope='session')
def anyio_backend() -> str:
    return 'asyncio'


@pytest.fixture(scope='session', autouse=True)
async def setup_db() -> AsyncIterator[None]:
    await init_db(test_container)

    yield

    engine = await test_container.get(AsyncEngine)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


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

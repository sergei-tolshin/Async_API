import asyncio
import json
from dataclasses import dataclass
from pathlib import Path

import aiohttp
import aioredis
import pytest
from elasticsearch import AsyncElasticsearch
from multidict import CIMultiDictProxy

from .settings import config
from .utils.utils import build_url


@dataclass
class HTTPResponse:
    body: dict
    headers: CIMultiDictProxy[str]
    status: int


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope='session')
async def es_client():
    client = AsyncElasticsearch(hosts=config.ELASTIC_URL)
    yield client
    await client.close()


@pytest.fixture(scope='session')
async def cache():
    client = await aioredis.create_redis_pool(
        (config.REDIS_HOST, config.REDIS_PORT),
        minsize=10,
        maxsize=20)
    await client.flushdb()
    yield client
    client.close()
    await client.wait_closed()


@pytest.fixture(scope='session')
async def session():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest.fixture
def make_get_request(session):
    async def inner(path: str, params: dict = None) -> HTTPResponse:
        params = params or {}
        url = build_url(config.SERVICE_URL, config.API_URL, path)
        async with session.get(url, params=params) as response:
            return HTTPResponse(
                body=await response.json(),
                headers=response.headers,
                status=response.status,
            )
    return inner


# https://stackoverflow.com/questions/50329629/how-to-access-a-json-filetest-data-like-config-json-in-conftest-py
@pytest.fixture
def read_case(request):
    async def inner(file_name: str) -> dict:
        file = Path(config.BASE_DIR, config.TEST_DATA_PATH, file_name)
        with file.open(encoding='utf-8') as fp:
            case_data = json.load(fp)
        return case_data
    return inner

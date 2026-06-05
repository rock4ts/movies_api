from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

import aiohttp
import jwt
import pytest
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis

from .settings import es_test_settings, jwt_test_settings, redis_test_settings, webapp_test_settings


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def es_client():
    es_client = AsyncElasticsearch(hosts=es_test_settings.elastic_url, verify_certs=False)
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session", autouse=True)
async def setup_es_indexes(es_client: AsyncElasticsearch):
    index_definitions = (
        (es_test_settings.movies_index, es_test_settings.movies_mapping),
        (es_test_settings.genres_index, es_test_settings.genres_mapping),
        (es_test_settings.persons_index, es_test_settings.persons_mapping),
    )

    for index_name, mapping in index_definitions:
        exists = await es_client.indices.exists(index=index_name)
        if exists:
            await es_client.indices.delete(index=index_name)
        await es_client.indices.create(index=index_name, body=mapping)


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def es_mock_data(es_client: AsyncElasticsearch):

    async def inner(index: str, es_data: dict[str, Any] | list[dict[str, Any]]):

        index_ops = []
        if isinstance(es_data, list):
            for row in es_data:
                data = {"_index": index, "_id": row["id"], "_source": row}
                index_ops.append(data)
        else:
            data = {"_index": index, "_id": es_data["id"], "_source": es_data}
            index_ops.append(data)
        indexed, errors = await async_bulk(client=es_client, actions=index_ops, refresh=True)

        if errors:
            raise Exception("Ошибка записи данных в Elasticsearch")

    return inner


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def es_destroy_mock_data(es_client: AsyncElasticsearch):

    async def inner(index: str):

        response = await es_client.delete_by_query(
            index=index, body={"query": {"match_all": {}}}, conflicts="proceed", refresh=True
        )
        if response.get("failures"):
            raise Exception(
                f"Ошибка удаления данных в индексе {index}: ", f'{response["failures"]}'
            )

    return inner


@pytest_asyncio.fixture(loop_scope="session", autouse=True)
async def clear_index(request, es_client: AsyncElasticsearch):
    """
    Для использования фикстуры нужно задекорировать тест по примеру:
    @pytest.mark.clear_index(index_name=es_test_settings.<NAME>_index)
    """
    marker = request.node.get_closest_marker("clear_index")

    if not marker:
        return

    index_name = marker.kwargs.get("index_name")
    if not index_name:
        return

    response = await es_client.delete_by_query(
        index=index_name, body={"query": {"match_all": {}}}, conflicts="proceed"
    )
    if response.get("failures"):
        raise Exception(
            f"Ошибка удаления данных в индексе {index_name}: ", f'{response["failures"]}'
        )


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def http_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def make_get_request(http_client: aiohttp.ClientSession):

    async def inner(
        endpoint: str,
        query_data: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ):
        url = webapp_test_settings.service_url + endpoint
        response = await http_client.get(url, params=query_data, headers=headers)
        body = await response.json()
        status = response.status
        return body, status

    return inner


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def make_access_token():
    private_key_path = Path(jwt_test_settings.private_key_path)
    jwt_algorithm = jwt_test_settings.jwt_algorithm

    if not private_key_path.exists():
        pytest.exit(f"JWT private key not found: {private_key_path}", returncode=1)

    private_key = private_key_path.read_text()

    def inner(
        access_labels: list[str] | None = None,
        is_superuser: bool = False,
        expires_in_minutes: int = 30,
    ) -> str:
        now = datetime.now(UTC)
        payload = {
            "type": "access",
            "is_superuser": is_superuser,
            "role": None,
            "access_labels": access_labels or [],
            "sub": str(uuid4()),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=expires_in_minutes)).timestamp()),
            "jti": str(uuid4()),
            "tv": 1,
        }
        try:
            return jwt.encode(payload, private_key, algorithm=jwt_algorithm)
        except NotImplementedError as err:
            pytest.skip(str(err))

    return inner


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def redis_client():
    r = Redis(host=redis_test_settings.redis_host, port=redis_test_settings.redis_port)
    yield r
    await r.aclose()


@pytest_asyncio.fixture(scope="function", loop_scope="session", autouse=True)
async def clear_cache(redis_client: Redis):
    yield
    await redis_client.flushdb()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def clear_cache_callable(redis_client: Redis):
    async def inner():
        await redis_client.flushdb()

    return inner


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def clear_cache_by_prefix(redis_client: Redis):

    async def inner(prefix):
        pattern = f"{prefix}:*"
        async for key in redis_client.scan_iter(pattern):
            await redis_client.delete(key)

    return inner

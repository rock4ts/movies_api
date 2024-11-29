from contextlib import asynccontextmanager

import aiohttp
import pytest_asyncio

from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from src.settings import es_test_settings, webapp_test_settings


@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def es_client():
    es_client = AsyncElasticsearch(
        hosts=es_test_settings.elastic_url, verify_certs=False
    )
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(scope='session', loop_scope='session', autouse=True)
async def es_indexes(es_client: AsyncElasticsearch):
    indexes_and_mappings = [
        (es_test_settings.genres_index, es_test_settings.genres_mapping),
        (es_test_settings.movies_index, es_test_settings.movies_mapping),
        (es_test_settings.persons_index, es_test_settings.persons_mapping)
    ]

    for index, mapping in indexes_and_mappings:
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)

        await es_client.indices.create(index=index, body=mapping)


@pytest_asyncio.fixture
def es_mock_data(es_client: AsyncElasticsearch):

    @asynccontextmanager
    async def inner(index: str, es_data: list[dict]):
        bulk_query = []
        try:
            for row in es_data:
                data = {'_index': index, '_id': row['id']}
                data.update({'_source': row})
                bulk_query.append(data)

            updated, errors = await async_bulk(
                client=es_client,
                actions=bulk_query,
                refresh=True
                )
            if errors:
                raise Exception('Ошибка записи данных в Elasticsearch')

            yield

        finally:
            bulk_query = []
            for row in es_data:
                bulk_query.append(
                    {'_op_type': 'delete', "_index": index, "_id": row["id"]}
                    )

            deleted, errors = await async_bulk(
                client=es_client,
                actions=bulk_query,
                refresh=True
                )
            if errors:
                raise Exception('Ошибка удаления данных в Elasticsearch')

    return inner


@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def http_client():
    session = aiohttp.ClientSession()
    yield session
    await session.close()


@pytest_asyncio.fixture
def make_get_request(http_client: aiohttp.ClientSession):

    async def inner(endpoint: str, query_data: dict | None = None):
        url = webapp_test_settings.service_url + endpoint
        response = await http_client.get(url, params=query_data)
        body = await response.json()
        status = response.status
        return body, status

    return inner

from contextlib import asynccontextmanager
import aiohttp
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from src.settings import es_test_settings, webapp_test_settings


@pytest_asyncio.fixture(
        name='es_client', scope='session', loop_scope='session'
        )
async def es_client():
    es_client = AsyncElasticsearch(
        hosts=es_test_settings.elastic_url, verify_certs=False
    )
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(
        name='es_create_indexes',
        scope='session',
        loop_scope='session',
        autouse=True
        )
async def es_create_indexes(es_client: AsyncElasticsearch):
    indexes_and_mappings = [
        (es_test_settings.genres_index, es_test_settings.genres_mapping),
        (es_test_settings.movies_index, es_test_settings.movies_mapping),
        (es_test_settings.persons_index, es_test_settings.persons_mapping)
    ]

    for index, mapping in indexes_and_mappings:
        if await es_client.indices.exists(index=index):
            await es_client.indices.delete(index=index)

        await es_client.indices.create(index=index, body=mapping)


@pytest_asyncio.fixture(name='es_mock_data')
def es_mock_data(es_client: AsyncElasticsearch):

    @asynccontextmanager
    async def inner(actions: list[dict]):
        try:
            updated, errors = await async_bulk(
                client=es_client,
                actions=actions,
                refresh=True
                )
            if errors:
                raise Exception('Ошибка записи данных в Elasticsearch')

            yield

        finally:
            data_to_delete = [
                {"delete": {"_index": item['_index'], "_id": item["_id"]}}
                for item in actions
                ]
            deleted, errors = await async_bulk(
                client=es_client,
                actions=data_to_delete,
                refresh=True
                )
            if errors:
                raise Exception('Ошибка удаленя данных в Elasticsearch')

    return inner


@pytest_asyncio.fixture(name='make_get_request')
def make_get_request():

    async def inner(endpoint: str, query_data: dict | None = None):
        session = aiohttp.ClientSession()
        url = webapp_test_settings.service_url + endpoint
        async with session.get(url, params=query_data) as response:
            body = await response.json()
            status = response.status
        await session.close()
        return body, status

    return inner

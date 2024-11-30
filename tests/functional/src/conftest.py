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


@pytest_asyncio.fixture(scope='session', loop_scope='session')
def es_mock_data(es_client: AsyncElasticsearch):

    async def inner(index: str, es_data: dict | list[dict]):

        index_ops = []
        if isinstance(es_data, list):
            for row in es_data:
                data = {'_index': index, '_id': row['id'], '_source': row}
                index_ops.append(data)
        else:
            data = {'_index': index, '_id': es_data['id'], '_source': es_data}
            index_ops.append(data)
        indexed, errors = await async_bulk(
            client=es_client,
            actions=index_ops,
            refresh=True
            )

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest_asyncio.fixture(scope='session', loop_scope='session')
def es_destroy_mock_data(es_client: AsyncElasticsearch):

    async def inner(index: str):

        response = await es_client.delete_by_query(
                index=index,
                body={"query": {"match_all": {}}},
                conflicts="proceed"
            )
        if response.get("failures"):
            raise Exception(
                f'Ошибка удаления данных в индексе {index}: ',
                f'{response["failures"]}'
            )

    return inner


@pytest_asyncio.fixture(scope='session', loop_scope='session')
async def clear_index(request, es_client: AsyncElasticsearch):
    '''
    Для использования фикстуры нужно задекорировать тест по примеру:
    @pytest.mark.clear_index(index_name=es_test_settings.<NAME>_index)
    '''
    marker = request.node.get_closest_marker("clear_index")

    if not marker:
        return

    index_name = marker.kwargs.get("index_name")
    if not index_name:
        return
    
    response = await es_client.delete_by_query(
        index=index_name,
        body={"query": {"match_all": {}}},
        conflicts="proceed"
    )
    if response.get("failures"):
        raise Exception(
            f'Ошибка удаления данных в индексе {index_name}: ',
            f'{response["failures"]}'
        )


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

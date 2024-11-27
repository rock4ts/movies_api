import json
import os
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(name='es_client', loop_scope='session')
async def es_client():
    es_client = AsyncElasticsearch(
        hosts=test_settings.elastic_url, verify_certs=False
    )
    yield es_client
    await es_client.close()


@pytest_asyncio.fixture(name='es_write_data')
def es_write_data(es_client):
    async def inner(data: list[dict], es_index: str):
        if await es_client.indices.exists(index=es_index):
            await es_client.indices.delete(index=es_index)
        schema_index = test_settings.es_index_mapping.get(es_index)
        # Загрузим схему в тело запроса
        json_schema_path = os.getenv(
            "JSON_SCHEMA_PATH", "tests/functional/elastic/schema"
        )
        with open(f"{json_schema_path}/{schema_index}", "r") as f:
            body = json.load(f)
        await es_client.indices.create(index=es_index, body=body)

        updated, errors = await async_bulk(client=es_client, actions=data)

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')
    return inner

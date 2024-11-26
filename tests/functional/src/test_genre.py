import uuid

import aiohttp
import pytest
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk

from tests.functional.settings import test_settings

INDEX_NAME = 'genres'

@pytest.mark.asyncio
async def test_get_genres_all():
    # es_data = [
    #     {
    #         'id': str(uuid.uuid4()),
    #         'name': "Drama"
    #     },
    #     {
    #         'id': str(uuid.uuid4()),
    #         'name': "Adventure"
    #     },
    #     {
    #         'id': str(uuid.uuid4()),
    #         'name': "Action"
    #     },
    # ]
    #
    # bulk_query: list[dict] = []
    # for row in es_data:
    #     data = {'_index': 'genres', '_id': row['id']}
    #     data.update({'_source': row})
    #     bulk_query.append(data)
    #
    # es_client = AsyncElasticsearch(hosts=test_settings.elastic_url, verify_certs=False)
    # if await es_client.indices.exists(index=INDEX_NAME):
    #     await es_client.indices.delete(index=INDEX_NAME)
    # await es_client.indices.create(index=INDEX_NAME, **test_settings.es_index_mapping)
    #
    # updated, errors = await async_bulk(client=es_client, actions=bulk_query)
    #
    # await es_client.close()
    #
    # if errors:
    #     raise Exception('Ошибка записи данных в Elasticsearch')

    async with aiohttp.ClientSession() as session:
        url = test_settings.service_url + '/api/v1/genres'
        async with session.get(url) as response:
            text = await response.text()
            assert response.status == 200, text
            body = await response.json()
            headers = response.headers

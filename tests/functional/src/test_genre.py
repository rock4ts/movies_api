import uuid

import aiohttp
import pytest

from tests.functional.settings import test_settings

INDEX_NAME = 'genres'


@pytest.mark.asyncio(loop_scope='session')
async def test_get_genres_all(es_write_data):
    es_data = [
        {
            'id': str(uuid.uuid4()),
            'name': "Drama"
        },
        {
            'id': str(uuid.uuid4()),
            'name': "Adventure"
        },
        {
            'id': str(uuid.uuid4()),
            'name': "Action"
        },
    ]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': 'genres', '_id': row['id']}
        data.update({'_source': row})
        bulk_query.append(data)

    # 2. Загружаем данные в ES
    await es_write_data(data=bulk_query, es_index=INDEX_NAME)

    async with aiohttp.ClientSession() as session:
        url = test_settings.service_url + '/api/v1/genres'
        async with session.get(url) as response:
            text = await response.text()
            assert response.status == 200, text
            body = await response.json()
            headers = response.headers

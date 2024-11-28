import uuid

import pytest

from src.settings import es_test_settings


@pytest.mark.asyncio
async def test_get_genres_request_empty(make_get_request):
    body, status = await make_get_request('/api/v1/genres')

    assert status == 200
    assert len(body) == 0


# @pytest.mark.asyncio
# async def test_get_genres_all(es_mock_data, make_get_request):
#     es_data = [
#         {
#             'id': str(uuid.uuid4()),
#             'name': "Drama"
#         },
#         {
#             'id': str(uuid.uuid4()),
#             'name': "Adventure"
#         },
#         {
#             'id': str(uuid.uuid4()),
#             'name': "Action"
#         },
#     ]

#     bulk_query: list[dict] = []
#     for row in es_data:
#         data = {'_index': es_test_settings.genres_index, '_id': row['id']}
#         data.update({'_source': row})
#         bulk_query.append(data)

#     async with es_mock_data(bulk_query):
#         body, status = await make_get_request('/api/v1/genres')

#     assert status == 200
#     assert len(body) == 3

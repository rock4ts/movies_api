# import uuid

# import pytest

# from src.settings import es_test_settings

# # Исключительно для теста
# # @pytest.mark.asyncio(loop_scope='session')
# # async def test_get_genres_request_empty(make_get_request):
# #     body, status = await make_get_request('/api/v1/genres')

# #     assert status == 200
# #     assert len(body) == 0


# @pytest.mark.asyncio(loop_scope='session')
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

#     async with es_mock_data(es_test_settings.genres_index, es_data):
#         body, status = await make_get_request('/api/v1/genres')

#     assert status == 200
#     assert len(body) == 3


# @pytest.mark.asyncio(loop_scope='session')
# async def test_get_genres_all_cached(make_get_request):

#     body, status = await make_get_request('/api/v1/genres')

#     assert status == 200
#     assert len(body) == 3

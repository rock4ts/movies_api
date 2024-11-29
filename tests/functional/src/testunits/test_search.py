import uuid

import pytest

from src.settings import es_test_settings


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        ({'query': 'The Star'},{'status': 200, 'length': 5}),
        ({'query': 'Mashed potato'}, {'status': 200, 'length': 0})
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_search(
    es_mock_data, make_get_request, query_data, expected_answer
    ):

    es_data = [{
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genres': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72c59f4e3f95', 'name': 'Action'},
            {'id': 'ef86b8ff-3c82-4d31-ad8e-99c59f4e3f95', 'name': 'Sci-Fi'}
        ],
        'title': 'The Star',
        'description': 'New World',
        'directors_names': ["Tom"],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'directors': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'full_name': 'Tom'},
        ],
        'actors': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'full_name': 'Ann'},
            {'id': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'full_name': 'Bob'}
        ],
        'writers': [
            {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'full_name': 'Ben'},
            {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'full_name': 'Howard'}
        ],
    } for _ in range(5)]

    async with es_mock_data(es_test_settings.movies_index, es_data):
        body, status = await make_get_request(
            '/api/v1/films/search',
            query_data
            )

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']

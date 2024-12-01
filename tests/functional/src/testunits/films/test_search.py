import uuid
import pytest

from src.settings import es_test_settings


FILM_COLLECTION: dict = {
    "7f5c7fa0-87b8-43d8-89f4-b3d617f86c46": "The Star wars 2022",
    "5e524cb4-ca24-4024-9976-43db53cac248": "The Ship ment 1993",
    "d8a1b05e-90c0-4878-877d-ea126417a1db": "The Sunset down",
    "cae0d911-4fcd-4fca-89df-f93042495ea8": "The Space is broken",
    "6f314893-a13d-48d6-b329-f598be4b5e4a": "The Space in danger"
}

FILM_INVALID_IDS: tuple = (
    'bb248af1-8e37-4c59',
    '4856a731-a980-4f74',
    '26fd48d4-51b4-463e',
    'afd527bf-521c-47f5',
    '841df630-aa62-4020'
)

ES_DATA: list[dict] = [
    {
        'id': id_,
        'imdb_rating': 8.5,
        'genres': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72c59f4e3f95', 'name': 'Action'},
            {'id': 'ef86b8ff-3c82-4d31-ad8e-99c59f4e3f95', 'name': 'Sci-Fi'}
        ],
        'title': title_,
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
            {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'full_name': 'How'}
        ],
    } for id_, title_ in FILM_COLLECTION.items()
]

ES_BIG_DATA = [
    {
        'id': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genres': [
            {'id': 'ef86b8ff-3c82-4d31-ad8e-72c59f4e3f95', 'name': 'Action'},
            {'id': 'ef86b8ff-3c82-4d31-ad8e-99c59f4e3f95', 'name': 'Sci-Fi'}
        ],
        'title': 'Dummy movies',
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
            {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'full_name': 'How'}
        ],
    } for _ in range(15)
]


# =========== Elastic data tests ===========
@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        ({'query': 'Star'}, {'status': 200, 'length': 1}),
        ({'query': 'Space'}, {'status': 200, 'length': 2}),
        ({'genre': "ef86b8ff-3c82-4d31-ad8e-72c59f4e3f95"},
         {'status': 200, 'length': 5}
         ),
        ({'sort': '-imdb_rating'}, {'status': 200, 'length': 5}),
        ({'query': 'Mashed potato'}, {'status': 200, 'length': 0}),
        ({'genre': 'not uuid string'}, {'status': 422, 'length': 1})
    ]
)
@pytest.mark.clear_index(index_name=es_test_settings.movies_index)
@pytest.mark.asyncio(loop_scope='session')
async def test_search(
    es_mock_data, make_get_request, query_data, expected_answer
):

    await es_mock_data(es_test_settings.movies_index, ES_DATA)

    body, status = await make_get_request(
        '/api/v1/films/search',
        query_data
    )


    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        ({'page_size': 3, 'page_number': 1}, {'status': 200, 'length': 3}),
        ({'page_size': 10, 'page_number': 1}, {'status': 200, 'length': 10}),
        ({'page_size': 4, 'page_number': 1}, {'status': 200, 'length': 4}),
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_search_pages(
    es_mock_data, make_get_request, query_data, expected_answer
):

    await es_mock_data(es_test_settings.movies_index, ES_BIG_DATA)

    body, status = await make_get_request(
        '/api/v1/films/search',
        query_data
    )

    assert status == expected_answer['status']
    assert len(body) == expected_answer['length']


# =========== Cashe tests ===========
@pytest.mark.asyncio(loop_scope='session')
@pytest.mark.clear_index(index_name=es_test_settings.movies_index)
async def test_search_cached(
    es_mock_data,
    es_destroy_mock_data,
    clear_cache_by_prefix,
    make_get_request
    ):

    query_data = {'query': 'Star'}

    await es_mock_data(es_test_settings.movies_index, ES_DATA)

    es_body, status = await make_get_request(
        '/api/v1/films/search',
        query_data
    )

    await es_destroy_mock_data(es_test_settings.movies_index)

    assert status == 200
    assert len(es_body) == 1


    cached_body, status = await make_get_request(
        '/api/v1/films/search',
        query_data
    )

    assert status == 200
    assert len(cached_body) == 1

    await clear_cache_by_prefix(es_test_settings.movies_index)

    empty_body, status = await make_get_request(
        '/api/v1/films/search',
        query_data
    )

    assert status == 200
    assert len(empty_body) == 0

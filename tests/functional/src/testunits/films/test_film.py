import pytest

from src.settings import es_test_settings

FILM_IDS: tuple = (
    'bb248af1-8e37-4c59-866d-40ac6e10b36f',
    '4856a731-a980-4f74-9b63-87271f54c4a5',
    '26fd48d4-51b4-463e-a8a8-8217da589c05',
    'afd527bf-521c-47f5-a3cb-b49318196398',
    '841df630-aa62-4020-9f73-d3f11944916b'
)

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
            {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'full_name': 'How'}
        ],
    } for id_ in FILM_IDS
]


# =========== Elastic data tests ===========
# GET ALL FILMS
@pytest.mark.asyncio(loop_scope='session')
async def test_get_films_all(es_mock_data, make_get_request):

    await es_mock_data(es_test_settings.movies_index, ES_DATA)
    
    body, status = await make_get_request('/api/v1/films')

    assert status == 200
    assert len(body) == 5


# GET FILM BY ID
@pytest.mark.parametrize(
    'film_ids, expected_answer',
    [
        (
            {'film_id': id_}, {'status': 200}
        ) for id_ in FILM_IDS
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_get_films_by_id(
    make_get_request, film_ids, expected_answer
):

    url = f'/api/v1/films/{film_ids['film_id']}'

    body, status = await make_get_request(url)

    assert status == expected_answer['status']
    assert body['uuid'] == film_ids['film_id']


# TEST VALIDATION FOR GET FILM BY ID
@pytest.mark.parametrize(
    'film_ids, expected_answer',
    [
        (
            {'film_id': id_}, {'status': 422}
        ) for id_ in FILM_INVALID_IDS
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_validation_films_by_id(
    make_get_request, film_ids, expected_answer
):

    url = f'/api/v1/films/{film_ids['film_id']}'

    body, status = await make_get_request(url)

    assert status == expected_answer['status']


# =========== Cashe tests ===========
@pytest.mark.clear_index(index_name=es_test_settings.movies_index)
@pytest.mark.asyncio(loop_scope='session')
async def test_get_films_all_cached(make_get_request):

    body, status = await make_get_request('/api/v1/films')

    assert status == 200
    assert len(body) == 5


@pytest.mark.asyncio(loop_scope='session')
async def test_get_films_by_id_cached(
    es_mock_data,
    es_destroy_mock_data,
    clear_cache_by_prefix,
    make_get_request,
    ):

    await es_mock_data(es_test_settings.movies_index, ES_DATA)

    for id_ in FILM_IDS:

        es_body, status = await make_get_request(f'/api/v1/films/{id_}')

        assert status == 200
        assert es_body['uuid'] == id_

    await es_destroy_mock_data(es_test_settings.movies_index)

    for id_ in FILM_IDS:
        cached_body, status = await make_get_request(f'/api/v1/films/{id_}')

        assert status == 200
        assert cached_body['uuid'] == id_

    await clear_cache_by_prefix(es_test_settings.movies_index)

    for id_ in FILM_IDS:
        empty_body, status = await make_get_request(f'/api/v1/films/{id_}')
        assert status == 404

import uuid

import pytest_asyncio

from tests.functional.settings import es_test_settings

TARGET_PERSON_NAME = "Test Testovich"
ROLE_GROUPS = ['directors', 'actors', 'writers']
FILMS_PER_GROUP = 5
TARGET_PERSON_FILMS_NUMBER = len(ROLE_GROUPS) * FILMS_PER_GROUP

DUMMY_PERSON_NAME = "Dummy"
DUMMY_FILMS_NUMBER = 5
DUMMY_PERSON_NUMBER_FACTOR = 5
DUMMY_PERSONS_NUMBER = 2 * 5
ALL_LOADED_PERSONS_COUNT = DUMMY_PERSONS_NUMBER + 1



@pytest_asyncio.fixture(scope='package')
def target_person_data():
    return {'id': str(uuid.uuid4()), 'full_name': TARGET_PERSON_NAME}


@pytest_asyncio.fixture(scope='package')
def non_existent_person_data():
    return {'id': str(uuid.uuid4()), 'full_name': "Yandex Practicumovich"}


@pytest_asyncio.fixture(scope='package')
def dummy_person_factory():

    def inner():
        return {'id': str(uuid.uuid4()), 'full_name': DUMMY_PERSON_NAME}

    return inner


@pytest_asyncio.fixture(scope='package')
def dummy_persons_data(dummy_person_factory):
    data = []
    for _ in range(DUMMY_PERSONS_NUMBER):
        dummy_person = dummy_person_factory()
        data.append(dummy_person)
    return data


@pytest_asyncio.fixture(scope='package')
def dummy_film_factory():

    def inner():
        film = {
            'id': str(uuid.uuid4()),
            'imdb_rating': 8.5,
            'genres': [
                {'id': 'ef86b8ff-3c82-4d31-ad8e-72c59f4e3f95', 'name': 'Action'},
                {'id': 'ef86b8ff-3c82-4d31-ad8e-99c59f4e3f95', 'name': 'Sci-Fi'}
            ],
            'title': 'The Star',
            'description': 'New World',
            'directors': [
                {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b6', 'name': 'Tom'}
            ],
            'actors': [
                {'id': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'name': 'Ben'},
            ],
            'writers': [
                {'id': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'name': 'Howard'}
            ],
        }
        return film

    return inner


@pytest_asyncio.fixture(scope='package')
def person_film_factory(dummy_film_factory):

    def inner(role_group, target_person_data):
        film_data = dummy_film_factory()
        # movies index expects nested person docs with "name", not "full_name"
        film_data[role_group] = [
            {"id": target_person_data["id"], "name": target_person_data["full_name"]}
        ]
        return film_data

    return inner


@pytest_asyncio.fixture(scope='package', loop_scope='session')
async def target_person_films_data(person_film_factory, target_person_data):
    data = []
    for group in ROLE_GROUPS:
        for _ in range(FILMS_PER_GROUP):
            new_film_data = person_film_factory(group, target_person_data)
            data.append(new_film_data)
    return data


@pytest_asyncio.fixture(scope='package', loop_scope='session')
async def dummy_films_data(dummy_film_factory):
    data = []
    for _ in range(DUMMY_FILMS_NUMBER):
        dummy_film = dummy_film_factory()
        data.append(dummy_film)
    return data



@pytest_asyncio.fixture(scope='package')
def index_and_data_pairs(
    target_person_data,
    dummy_persons_data,
    target_person_films_data,
    dummy_films_data
    ):
    pairs = [
        (es_test_settings.persons_index, target_person_data),
        (es_test_settings.persons_index, dummy_persons_data),
        (es_test_settings.movies_index, target_person_films_data),
        (es_test_settings.movies_index, dummy_films_data)
        ]
    return pairs


def _setup_es_mock_persons(
    es_mock_data,
    es_destroy_mock_data,
    index_and_data_pairs: list[tuple[str, list]]
):
    async def setup():
        for index, data in index_and_data_pairs:
            await es_mock_data(index, data)

    async def teardown():
        for index, _ in index_and_data_pairs:
            await es_destroy_mock_data(index)

    return setup, teardown


@pytest_asyncio.fixture(scope='module', loop_scope='session')
async def es_mock_persons_module(es_mock_data, es_destroy_mock_data, index_and_data_pairs):
    setup, teardown = _setup_es_mock_persons(
        es_mock_data, es_destroy_mock_data, index_and_data_pairs
        )

    await setup()
    yield
    await teardown()


@pytest_asyncio.fixture(scope='function', loop_scope='session')
async def es_mock_persons_function(es_mock_data, es_destroy_mock_data, index_and_data_pairs):
    setup, teardown = _setup_es_mock_persons(
        es_mock_data, es_destroy_mock_data, index_and_data_pairs
        )

    await setup()
    yield
    await teardown()

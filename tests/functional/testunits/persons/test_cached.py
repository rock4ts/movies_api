from http import HTTPStatus

import pytest
import pytest_asyncio

from tests.functional.settings import es_test_settings

from .conftest import TARGET_PERSON_FILMS_NUMBER, TARGET_PERSON_NAME


@pytest_asyncio.fixture(scope='function', loop_scope='session', autouse=True)
async def es_mock_persons_function_auto(es_mock_persons_function):
    pass


@pytest.mark.asyncio(loop_scope='session')
async def test_person_search_uses_cache(
    make_get_request,
    target_person_data,
    es_destroy_mock_data,
    clear_cache_by_prefix
    ):
    query_data = {"query": TARGET_PERSON_NAME}

    persons_from_es, _ = await make_get_request('/api/v1/persons/search', query_data)

    assert len(persons_from_es) == 1
    assert persons_from_es[0]['uuid'] == target_person_data['id']
    
    await es_destroy_mock_data(es_test_settings.persons_index)

    persons_from_cache, _ = await make_get_request('/api/v1/persons/search', query_data)

    assert len(persons_from_cache) == 1
    assert persons_from_cache[0]['uuid'] == target_person_data['id']

    await clear_cache_by_prefix(es_test_settings.persons_index)

    persons_deleted, _ = await make_get_request('/api/v1/persons/search', query_data)

    assert len(persons_deleted) == 0


@pytest.mark.asyncio(loop_scope='session')
async def test_persons_films_uses_cache(
    make_get_request,
    target_person_data,
    es_destroy_mock_data,
    clear_cache_by_prefix
    ):

    films_from_es, _ = await make_get_request(
        f"/api/v1/persons/{target_person_data['id']}/film"
        )

    assert len(films_from_es) == TARGET_PERSON_FILMS_NUMBER

    await es_destroy_mock_data(es_test_settings.movies_index)
    films_from_cache, _ = await make_get_request(
        f"/api/v1/persons/{target_person_data['id']}/film"
    )

    assert len(films_from_cache) == TARGET_PERSON_FILMS_NUMBER


    await clear_cache_by_prefix(es_test_settings.persons_index)
    films_deleted, _ = await make_get_request(
        f"/api/v1/persons/{target_person_data['id']}/film"
    )

    assert len(films_deleted) == 0


@pytest.mark.asyncio(loop_scope='session')
async def test_person_details(
    make_get_request,
    target_person_data,
    es_destroy_mock_data,
    clear_cache_by_prefix
    ):
    person_from_es, _ = await make_get_request(
        f"/api/v1/persons/{target_person_data['id']}"
        )

    assert person_from_es['uuid'] == target_person_data['id']

    await es_destroy_mock_data(es_test_settings.persons_index)
    person_from_cache, _ = await make_get_request(
        f"/api/v1/persons/{target_person_data['id']}"
        )

    assert person_from_cache['uuid'] == target_person_data['id']

    await clear_cache_by_prefix(es_test_settings.persons_index)
    _, status_not_found = await make_get_request(
        f"/api/v1/persons/{target_person_data['id']}"
        )

    assert status_not_found == HTTPStatus.NOT_FOUND

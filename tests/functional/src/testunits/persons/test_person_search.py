from http import HTTPStatus

import pytest
import pytest_asyncio

from src.testunits.persons.conftest import (ALL_LOADED_PERSONS_COUNT,
                                            DUMMY_PERSON_NAME,
                                            DUMMY_PERSON_NUMBER_FACTOR,
                                            DUMMY_PERSONS_NUMBER,
                                            TARGET_PERSON_NAME)


@pytest_asyncio.fixture(scope='module', loop_scope='session', autouse=True)
async def es_mock_persons_module_auto(es_mock_persons_module):
    pass


@pytest.mark.asyncio(loop_scope='session')
async def test_persons_search_without_query_returns_all(make_get_request):
    all_persons = []
    query_data = {"page_size": 5, "page_number": 1}
    batch, _ = await make_get_request('/api/v1/persons/search', query_data)
    while batch:
        all_persons.extend(batch)
        query_data['page_number'] += 1
        batch, _ = await make_get_request('/api/v1/persons/search', query_data)

    assert len(all_persons) == ALL_LOADED_PERSONS_COUNT


@pytest.mark.parametrize(
    'query_data', [{'query': TARGET_PERSON_NAME}, {'query': 'Dummy'}]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_persons_search(make_get_request, query_data):

    persons, status = await make_get_request('/api/v1/persons/search', query_data)

    assert status == HTTPStatus.OK
    assert len(persons) >= 1

    for person in persons:
        assert query_data['query'] in person["full_name"]



@pytest.mark.asyncio(loop_scope='session')
async def test_search_result_can_be_limited_by_size(make_get_request):
    all_dummies_query = {"query": DUMMY_PERSON_NAME}
    all_dummies, _ = await make_get_request('/api/v1/persons/search', all_dummies_query)

    all_dummies_count = len(all_dummies)

    assert all_dummies_count > 1
    assert all_dummies_count == DUMMY_PERSONS_NUMBER

    all_minus_one_query = {"query": DUMMY_PERSON_NAME, "page_size": all_dummies_count - 1}
    all_minus_one, _ = await make_get_request('/api/v1/persons/search', all_minus_one_query)

    all_minus_one_count = len(all_minus_one)

    assert all_minus_one_count > 1
    assert all_minus_one_count == DUMMY_PERSONS_NUMBER - 1


@pytest.mark.asyncio(loop_scope='session')
async def test_search_result_can_be_paginated(make_get_request):
    all_dummies_query = {"query": DUMMY_PERSON_NAME}
    all_dummies, _ = await make_get_request('/api/v1/persons/search', all_dummies_query)

    number_of_pages = DUMMY_PERSON_NUMBER_FACTOR
    page_size = DUMMY_PERSONS_NUMBER / number_of_pages

    all_dummies_from_pages = []
    for page in range(1, number_of_pages + 1):
        page_query = {"query": DUMMY_PERSON_NAME, "page_number": page, "page_size": page_size}
        dummies, _ = await make_get_request('/api/v1/persons/search', page_query)
        all_dummies_from_pages.extend(dummies)

    assert len(all_dummies) == len(all_dummies_from_pages)

    all_ids = [dummy['uuid'] for dummy in all_dummies]
    all_ids_from_pages = [dummy['uuid'] for dummy in all_dummies_from_pages]

    for id_ in all_ids:
        assert id_ in all_ids_from_pages

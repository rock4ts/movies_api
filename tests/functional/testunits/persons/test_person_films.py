from http import HTTPStatus

import pytest
import pytest_asyncio


@pytest_asyncio.fixture(scope='module', loop_scope='session', autouse=True)
async def es_mock_persons_module_auto(es_mock_persons_module):
    pass


@pytest.mark.asyncio(loop_scope='session')
async def test_not_added_person_films_returns_nothing(
    make_get_request, non_existent_person_data
    ):
    person_films, status = await make_get_request(
        f'/api/v1/persons/{non_existent_person_data["id"]}/films'
    )
    assert status == HTTPStatus.OK
    assert len(person_films) == 0


@pytest.mark.asyncio(loop_scope='session')
async def test_added_person_films_returns_expected_data(
    make_get_request, target_person_data, target_person_films_data
    ):
    person_films, status = await make_get_request(
        f'/api/v1/persons/{target_person_data["id"]}/films'
        )
    all_films, _ = await make_get_request('/api/v1/films')

    assert status == HTTPStatus.OK
    assert len(person_films) == len(target_person_films_data)
    assert len(all_films) > len(person_films)

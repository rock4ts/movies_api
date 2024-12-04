from http import HTTPStatus

import pytest
import pytest_asyncio


@pytest_asyncio.fixture(scope='module', loop_scope='session', autouse=True)
async def es_mock_persons_module_auto(es_mock_persons_module):
    pass


@pytest.mark.asyncio(loop_scope='session')
async def test_persons_can_be_found_by_id(
    make_get_request, target_person_data, non_existent_person_data
    ):
    body, person_found_status = await make_get_request(
        f'/api/v1/persons/{target_person_data["id"]}'
        )
    body, person_not_found_status = await make_get_request(
        f'/api/v1/persons/{non_existent_person_data["id"]}'
        )
    assert person_found_status == HTTPStatus.OK
    assert person_not_found_status == HTTPStatus.NOT_FOUND


@pytest.mark.asyncio(loop_scope='session')
async def test_person_details_returns_expected_data(
    make_get_request, target_person_films_data, target_person_data
    ):
    person, status = await make_get_request(
        f'/api/v1/persons/{target_person_data['id']}'
        )
    all_films, _ = await make_get_request('/api/v1/films')

    assert status == HTTPStatus.OK
    assert person["uuid"] == target_person_data['id']
    assert person["full_name"] == target_person_data['full_name']
    assert len(person['films']) == len(target_person_films_data)
    assert len(all_films) > len(person["films"])

import pytest
import pytest_asyncio


@pytest_asyncio.fixture(scope='module', loop_scope='session', autouse=True)
async def es_mock_persons_module_auto(es_mock_persons_module):
    pass


@pytest.mark.asyncio(loop_scope='session')
async def test_person_details_validates_path_uuid(make_get_request):
    bad_id = 'bad_id'
    body, status = await make_get_request(f'/api/v1/persons/{bad_id}')

    assert status == 422


@pytest.mark.asyncio(loop_scope='session')
async def test_person_films_validates_path_uuid(make_get_request):
    bad_id = 'bad_id'
    body, status = await make_get_request(f'/api/v1/persons/{bad_id}/film')

    assert status == 422


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [
        ({'page_number': 'a', 'page_size': 1,  'query': 'abc'}, 422),
        ({'page_number': 1, 'page_size': 'b',  'query': 'abc'}, 422),
        ({'page_number': 1, 'page_size': 1,  'query': 'abc'}, 200),
        ({'page_number': 0}, 422),
        ({'page_number': 100}, 200),
        ({'page_number': 101}, 422),
        ({'page_size': 0}, 422),
        ({'page_size': 100}, 200),
        ({'page_size': 101}, 422),
        ({'query': '???'}, 200),
        ({'query': -1}, 200),
        ({}, 200)
    ]
)
@pytest.mark.asyncio(loop_scope='session')
async def test_person_search_validates_query_params(
    make_get_request, query_data, expected_answer
    ):
    body, status = await make_get_request(f'/api/v1/persons/search', query_data)

    assert status == expected_answer

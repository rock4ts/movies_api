from http import HTTPStatus

import pytest

from tests.functional.settings import es_test_settings

from .genres_testdata import ES_DATA, NON_EXISTENT_ID


@pytest.mark.asyncio(loop_scope='session')
async def test_genres_get_by_id(es_mock_data, make_get_request):

    await es_mock_data(es_test_settings.genres_index, ES_DATA)

    body, genre_found_status = await make_get_request(
        f'/api/v1/genres/{ES_DATA[0]["id"]}'
        )
    body, genre_not_found_status = await make_get_request(
        f'/api/v1/genres/{NON_EXISTENT_ID}'
        )
    assert genre_found_status == HTTPStatus.OK
    assert genre_not_found_status == HTTPStatus.NOT_FOUND

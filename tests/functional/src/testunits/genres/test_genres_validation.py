from http import HTTPStatus

import pytest

from .genres_testdata import BAD_ID


@pytest.mark.asyncio(loop_scope='session')
async def test_genre_get_by_id_validation(make_get_request):
    body, status = await make_get_request(f'/api/v1/genres/{BAD_ID}')

    assert status == HTTPStatus.UNPROCESSABLE_ENTITY

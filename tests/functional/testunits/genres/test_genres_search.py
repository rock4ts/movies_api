import pytest

from tests.functional.settings import es_test_settings

from .genres_testdata import ES_DATA


@pytest.mark.clear_index(index_name=es_test_settings.genres_index)
@pytest.mark.asyncio(loop_scope='session')
async def test_search(es_mock_data, make_get_request):

    await es_mock_data(es_test_settings.genres_index, ES_DATA)

    all_genres, _ = await make_get_request('/api/v1/genres')

    assert len(all_genres) == len(ES_DATA)

from http import HTTPStatus

import pytest

from src.settings import es_test_settings

from .genres_testdata import ES_DATA


@pytest.mark.asyncio(loop_scope='session')
async def test_genre_get_by_id_cache(
        make_get_request,
        es_mock_data,
        es_destroy_mock_data,
        clear_cache_by_prefix
):
    await es_mock_data(es_test_settings.genres_index, ES_DATA)
    genre_from_es, _ = await make_get_request(f'/api/v1/genres/{ES_DATA[0]["id"]}')
    print(f'genre_from_es {genre_from_es}')

    assert genre_from_es['uuid'] == ES_DATA[0]['id']

    await es_destroy_mock_data(es_test_settings.genres_index)

    genre_from_cache, _ = await make_get_request(f'/api/v1/genres/{ES_DATA[0]["id"]}')

    assert genre_from_cache['uuid'] == ES_DATA[0]['id']

    await clear_cache_by_prefix(es_test_settings.genres_index)

    empty_body, status = await make_get_request(
        '/api/v1/genres')

    assert status == HTTPStatus.OK
    assert len(empty_body) == 0


@pytest.mark.asyncio(loop_scope='session')
async def test_genres_all_cache(
        make_get_request,
        es_mock_data,
        es_destroy_mock_data,
        clear_cache_by_prefix
):
    await es_mock_data(es_test_settings.genres_index, ES_DATA)

    genres_from_es, _ = await make_get_request('/api/v1/genres')

    assert len(genres_from_es) == len(ES_DATA)

    await es_destroy_mock_data(es_test_settings.genres_index)
    genres_from_cache, _ = await make_get_request('/api/v1/genres')

    assert len(genres_from_cache) == len(ES_DATA)

    await clear_cache_by_prefix(es_test_settings.genres_index)
    genres_deleted, _ = await make_get_request('/api/v1/genres')

    assert len(genres_deleted) == 0

from http import HTTPStatus
from typing import Any

import pytest
from tests.functional.settings import es_test_settings

FILM_IDS: tuple[str, ...] = (
    "bb248af1-8e37-4c59-866d-40ac6e10b36f",
    "4856a731-a980-4f74-9b63-87271f54c4a5",
    "26fd48d4-51b4-463e-a8a8-8217da589c05",
    "afd527bf-521c-47f5-a3cb-b49318196398",
    "841df630-aa62-4020-9f73-d3f11944916b",
)

FILM_INVALID_IDS: tuple[str, ...] = (
    "bb248af1-8e37-4c59",
    "4856a731-a980-4f74",
    "26fd48d4-51b4-463e",
    "afd527bf-521c-47f5",
    "841df630-aa62-4020",
)

ES_DATA: list[dict[str, Any]] = [
    {
        "id": id_,
        "imdb_rating": 8.5,
        "genres": [
            {"id": "ef86b8ff-3c82-4d31-ad8e-72c59f4e3f95", "name": "Action"},
            {"id": "ef86b8ff-3c82-4d31-ad8e-99c59f4e3f95", "name": "Sci-Fi"},
        ],
        "title": "The Star",
        "description": "New World",
        "directors": [
            {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Tom"},
        ],
        "actors": [
            {"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"},
            {"id": "fb111f22-121e-44a7-b78f-b19191810fbf", "name": "Bob"},
        ],
        "writers": [
            {"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"},
            {"id": "b45bd7bc-2e16-46d5-b125-983d356768c6", "name": "How"},
        ],
    }
    for id_ in FILM_IDS
]

ACCESS_FILM_IDS: dict[str, str] = {
    "free": "8ef89d95-0f0c-4d35-b3f5-03f37bb0d7bd",
    "premium": "2b5786bf-9884-4e36-8a88-fd9f15f7fe63",
    "vip": "618cd57a-ef5f-4f8a-9145-32ca374e39a5",
}

ACCESS_LABEL_ES_DATA: list[dict[str, Any]] = [
    {
        "id": ACCESS_FILM_IDS["free"],
        "imdb_rating": 7.1,
        "access_label": "free",
        "genres": [{"id": "ef86b8ff-3c82-4d31-ad8e-72c59f4e3f95", "name": "Action"}],
        "title": "Free Film",
        "description": "Accessible for everyone",
        "directors": [{"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Tom"}],
        "actors": [{"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"}],
        "writers": [{"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"}],
    },
    {
        "id": ACCESS_FILM_IDS["premium"],
        "imdb_rating": 8.1,
        "access_label": "premium",
        "genres": [{"id": "ef86b8ff-3c82-4d31-ad8e-72c59f4e3f95", "name": "Action"}],
        "title": "Premium Film",
        "description": "Accessible for premium users",
        "directors": [{"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Tom"}],
        "actors": [{"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"}],
        "writers": [{"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"}],
    },
    {
        "id": ACCESS_FILM_IDS["vip"],
        "imdb_rating": 9.1,
        "access_label": "vip",
        "genres": [{"id": "ef86b8ff-3c82-4d31-ad8e-72c59f4e3f95", "name": "Action"}],
        "title": "Vip Film",
        "description": "Accessible for vip users",
        "directors": [{"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Tom"}],
        "actors": [{"id": "ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95", "name": "Ann"}],
        "writers": [{"id": "caf76c67-c0fe-477e-8766-3ab3ff2574b5", "name": "Ben"}],
    },
]


# =========== Elastic data tests ===========
# GET ALL FILMS
@pytest.mark.asyncio(loop_scope="session")
async def test_get_films_all(es_mock_data, make_get_request):

    await es_mock_data(es_test_settings.movies_index, ES_DATA)

    body, status = await make_get_request("/api/v1/films")

    assert status == HTTPStatus.OK
    assert len(body) == 5


# GET FILM BY ID
@pytest.mark.parametrize(
    "film_ids, expected_answer", [({"film_id": id_}, {"status": HTTPStatus.OK}) for id_ in FILM_IDS]
)
@pytest.mark.asyncio(loop_scope="session")
async def test_get_films_by_id(make_get_request, film_ids, expected_answer):

    url = f"/api/v1/films/{film_ids['film_id']}"

    body, status = await make_get_request(url)

    assert status == expected_answer["status"]
    assert body["uuid"] == film_ids["film_id"]


# TEST VALIDATION FOR GET FILM BY ID
@pytest.mark.parametrize(
    "film_ids, expected_answer",
    [({"film_id": id_}, {"status": HTTPStatus.UNPROCESSABLE_ENTITY}) for id_ in FILM_INVALID_IDS],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_validation_films_by_id(make_get_request, film_ids, expected_answer):

    url = f"/api/v1/films/{film_ids['film_id']}"

    body, status = await make_get_request(url)

    assert status == expected_answer["status"]


# =========== Cashe tests ===========
@pytest.mark.clear_index(index_name=es_test_settings.movies_index)
@pytest.mark.asyncio(loop_scope="session")
async def test_get_films_all_cached(make_get_request):

    body, status = await make_get_request("/api/v1/films")

    assert status == HTTPStatus.OK
    assert len(body) == 5


@pytest.mark.asyncio(loop_scope="session")
async def test_get_films_by_id_cached(
    es_mock_data,
    es_destroy_mock_data,
    clear_cache_by_prefix,
    make_get_request,
):

    await es_mock_data(es_test_settings.movies_index, ES_DATA)

    for id_ in FILM_IDS:

        es_body, status = await make_get_request(f"/api/v1/films/{id_}")

        assert status == HTTPStatus.OK
        assert es_body["uuid"] == id_

    await es_destroy_mock_data(es_test_settings.movies_index)

    for id_ in FILM_IDS:
        cached_body, status = await make_get_request(f"/api/v1/films/{id_}")

        assert status == HTTPStatus.OK
        assert cached_body["uuid"] == id_

    await clear_cache_by_prefix(es_test_settings.movies_index)

    for id_ in FILM_IDS:
        empty_body, status = await make_get_request(f"/api/v1/films/{id_}")
        assert status == HTTPStatus.NOT_FOUND


@pytest.mark.clear_index(index_name=es_test_settings.movies_index)
@pytest.mark.parametrize(
    ("access_level", "expected_status"),
    [
        ("free", HTTPStatus.OK),
        ("premium", HTTPStatus.FORBIDDEN),
        ("vip", HTTPStatus.FORBIDDEN),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_get_film_details_anonymous_access(
    es_mock_data,
    make_get_request,
    access_level,
    expected_status,
):
    await es_mock_data(es_test_settings.movies_index, ACCESS_LABEL_ES_DATA)

    film_id = ACCESS_FILM_IDS[access_level]
    body, status = await make_get_request(f"/api/v1/films/{film_id}")

    assert status == expected_status
    if expected_status == HTTPStatus.OK:
        assert body["uuid"] == film_id
    else:
        assert body["detail"] == "film access error"


@pytest.mark.clear_index(index_name=es_test_settings.movies_index)
@pytest.mark.parametrize(
    ("token_labels", "expected_statuses"),
    [
        (
            ["free"],
            {
                "free": HTTPStatus.OK,
                "premium": HTTPStatus.FORBIDDEN,
                "vip": HTTPStatus.FORBIDDEN,
            },
        ),
        (
            ["premium"],
            {
                "free": HTTPStatus.FORBIDDEN,
                "premium": HTTPStatus.OK,
                "vip": HTTPStatus.FORBIDDEN,
            },
        ),
        (
            ["vip"],
            {
                "free": HTTPStatus.FORBIDDEN,
                "premium": HTTPStatus.FORBIDDEN,
                "vip": HTTPStatus.OK,
            },
        ),
        (
            ["free", "premium", "vip"],
            {
                "free": HTTPStatus.OK,
                "premium": HTTPStatus.OK,
                "vip": HTTPStatus.OK,
            },
        ),
    ],
)
@pytest.mark.asyncio(loop_scope="session")
async def test_get_film_details_jwt_access_labels(
    es_mock_data,
    make_get_request,
    make_access_token,
    token_labels,
    expected_statuses,
):
    await es_mock_data(es_test_settings.movies_index, ACCESS_LABEL_ES_DATA)

    token = make_access_token(access_labels=token_labels)
    headers = {"Authorization": f"Bearer {token}"}

    for label, expected_status in expected_statuses.items():
        film_id = ACCESS_FILM_IDS[label]
        body, status = await make_get_request(f"/api/v1/films/{film_id}", headers=headers)

        assert status == expected_status
        if expected_status == HTTPStatus.OK:
            assert body["uuid"] == film_id
        else:
            assert body["detail"] == "film access error"


@pytest.mark.clear_index(index_name=es_test_settings.movies_index)
@pytest.mark.asyncio(loop_scope="session")
async def test_get_film_details_jwt_superuser_access(
    es_mock_data,
    make_get_request,
    make_access_token,
):
    await es_mock_data(es_test_settings.movies_index, ACCESS_LABEL_ES_DATA)

    token = make_access_token(access_labels=[], is_superuser=True)
    headers = {"Authorization": f"Bearer {token}"}

    for film_id in ACCESS_FILM_IDS.values():
        body, status = await make_get_request(f"/api/v1/films/{film_id}", headers=headers)
        assert status == HTTPStatus.OK
        assert body["uuid"] == film_id

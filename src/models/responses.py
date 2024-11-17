"""Temporary Mock examples for all app endpoint according to API contract
All these examples will be returned as 200 response by default.
(e.g. Swagger --> Try it out)
TODO delete this file after finished service implementation!
"""
import uuid
import models


# Пример ответа для эндпоинта /films/{uuid}
class FilmDetailResponse:
    body = {
        "id": uuid.uuid4(),
        "title": "Test Film",
        "imdb_rating": 8.0,
        "description": "A captivating test film description.",
        "genres": [
            {"id": uuid.uuid4(), "name": "Adventure"},
            {"id": uuid.uuid4(), "name": "Comedy"}
        ],
        "actors": [
            {"id": uuid.uuid4(), "name": "John Doe"},
            {"id": uuid.uuid4(), "name": "Jane Doe"}
        ],
        "writers": [
            {"id": uuid.uuid4(), "name": "William Smith"}
        ],
        "directors": [
            {"id": uuid.uuid4(), "name": "Michael Bay"}
        ]
    }
    response = models.FilmDetail(**body)


# Пример ответа для эндпоинта /films
class FilmListResponse:
    body = [
        {"id": uuid.uuid4(), "title": "Film 1", "imdb_rating": 7.5},
        {"id": uuid.uuid4(), "title": "Film 2", "imdb_rating": 8.1}
    ]
    response = [models.Film(**item) for item in body]


# Пример ответа для эндпоинта /genres
class GenreListResponse:
    body = [
        {"id": uuid.uuid4(), "name": "Adventure"},
        {"id": uuid.uuid4(), "name": "Fantasy"},
        {"id": uuid.uuid4(), "name": "Comedy"}
    ]
    response = [models.Genre(**item) for item in body]


# Пример ответа для эндпоинта /films/search
class FilmSearchResponse:
    body = [
        {"id": uuid.uuid4(), "title": "Star Wars", "imdb_rating": 8.7},
        {"id": uuid.uuid4(), "title": "Star Trek", "imdb_rating": 7.8}
    ]
    response = [models.Film(**item) for item in body]


# Пример ответа для эндпоинта /persons/search
class PersonSearchResponse:
    body = [
        {
            "id": uuid.uuid4(),
            "full_name": "Harrison Ford",
            "films": [{"id": uuid.uuid4(), "roles": ["actor"]}]
        },
        {
            "id": uuid.uuid4(),
            "full_name": "Mark Hamill",
            "films": [{"id": uuid.uuid4(), "roles": ["actor"]}]
        }
    ]
    response = [models.Person(**item) for item in body]


# Пример ответа для эндпоинта /persons/{uuid}
class PersonDetailResponse:
    body = {
        "id": uuid.uuid4(),
        "full_name": "George Lucas",
        "films": [
            {"id": uuid.uuid4(), "roles": ["writer"]},
            {"id": uuid.uuid4(), "roles": ["director"]}
        ]
    }
    response = models.Person(**body)


# Пример ответа для эндпоинта /persons/{uuid}/film
class FilmListResponse:
    body = [
        {"id": uuid.uuid4(), "title": "Star Wars", "imdb_rating": 8.6},
        {"id": uuid.uuid4(), "title": "Indiana Jones", "imdb_rating": 8.4}
    ]
    response = [models.Film(**item) for item in body]


# Пример ответа для эндпоинта /genres/{uuid}
class GenreDetailResponse:
    body = {
        "id": uuid.uuid4(),
        "name": "Action"
    }
    response = models.Genre(**body)

"""Temporary Mock examples for all app endpoint according to API contract
All these examples will be returned as 200 response by default.
(e.g. Swagger --> Try it out)
TODO delete this file after finished service implementation!
"""
import uuid
from models.film import Film, FilmDetail, Genre, Person


# Пример ответа для эндпоинта /films/{uuid}
class FilmDetailResponse:
    body = {
        "uuid": uuid.uuid4(),
        "title": "Test Film",
        "imdb_rating": 8.0,
        "description": "A captivating test film description.",
        "genre": [
            {"uuid": uuid.uuid4(), "name": "Adventure"},
            {"uuid": uuid.uuid4(), "name": "Comedy"}
        ],
        "actors": [
            {"uuid": uuid.uuid4(), "full_name": "John Doe"},
            {"uuid": uuid.uuid4(), "full_name": "Jane Doe"}
        ],
        "writers": [
            {"uuid": uuid.uuid4(), "full_name": "William Smith"}
        ],
        "directors": [
            {"uuid": uuid.uuid4(), "full_name": "Michael Bay"}
        ]
    }
    response = FilmDetail(**body)


# Пример ответа для эндпоинта /films
class FilmListResponse:
    body = [
        {"uuid": uuid.uuid4(), "title": "Film 1", "imdb_rating": 7.5},
        {"uuid": uuid.uuid4(), "title": "Film 2", "imdb_rating": 8.1}
    ]
    response = [Film(**item) for item in body]


# Пример ответа для эндпоинта /genres
class GenreListResponse:
    body = [
        {"uuid": uuid.uuid4(), "name": "Adventure"},
        {"uuid": uuid.uuid4(), "name": "Fantasy"},
        {"uuid": uuid.uuid4(), "name": "Comedy"}
    ]
    response = [Genre(**item) for item in body]


# Пример ответа для эндпоинта /films/search
class FilmSearchResponse:
    body = [
        {"uuid": uuid.uuid4(), "title": "Star Wars", "imdb_rating": 8.7},
        {"uuid": uuid.uuid4(), "title": "Star Trek", "imdb_rating": 7.8}
    ]
    response = [Film(**item) for item in body]


# Пример ответа для эндпоинта /persons/search
class PersonSearchResponse:
    body = [
        {
            "uuid": uuid.uuid4(),
            "full_name": "Harrison Ford",
            "films": [{"uuid": uuid.uuid4(), "roles": ["actor"]}]
        },
        {
            "uuid": uuid.uuid4(),
            "full_name": "Mark Hamill",
            "films": [{"uuid": uuid.uuid4(), "roles": ["actor"]}]
        }
    ]
    response = [Person(**item) for item in body]


# Пример ответа для эндпоинта /persons/{uuid}
class PersonDetailResponse:
    body = {
        "uuid": uuid.uuid4(),
        "full_name": "George Lucas",
        "films": [
            {"uuid": uuid.uuid4(), "roles": ["writer"]},
            {"uuid": uuid.uuid4(), "roles": ["director"]}
        ]
    }
    response = Person(**body)


# Пример ответа для эндпоинта /persons/{uuid}/film
class PersonFilmListResponse:
    body = [
        {"uuid": uuid.uuid4(), "title": "Star Wars", "imdb_rating": 8.6},
        {"uuid": uuid.uuid4(), "title": "Indiana Jones", "imdb_rating": 8.4}
    ]
    response = [Film(**item) for item in body]


# Пример ответа для эндпоинта /genres/{uuid}
class GenreDetailResponse:
    body = {
        "uuid": uuid.uuid4(),
        "name": "Action"
    }
    response = Genre(**body)

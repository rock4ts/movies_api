import http
from typing import Annotated, Any
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
import jwt
from fastapi import Depends, HTTPException, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis

from app.core.config import settings
from app.db.clients import es, redis
from app.api.v1.request_models import (
    FilmListParams as ApiFilmListParamsModel,
    FilmSearchParams as ApiFilmSearchParamsModel,
    PersonSearchParams as ApiPersonSearchParamsModel,
)
from app.services.film import FilmService
from app.services.genre import GenreService
from app.services.person import PersonService
from app.services.schemas import (
    FilmListParamsDTO as ServiceFilmListParamsModel,
    FilmSearchParamsDTO as ServiceFilmSearchParamsModel,
    PersonSearchParamsDTO as ServicePersonSearchParamsModel,
)

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5
GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


@lru_cache()
def get_redis() -> Redis:
    return redis


@lru_cache()
def get_elastic() -> AsyncElasticsearch:
    return es


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic, settings.film_index)


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic, settings.genre_index)


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic, settings.person_index, settings.film_index)


def get_film_list_service_params(
    request_params: Annotated[ApiFilmListParamsModel, Query()],
) -> ServiceFilmListParamsModel:
    return ServiceFilmListParamsModel.model_validate(request_params.model_dump())


def get_film_search_service_params(
    request_params: Annotated[ApiFilmSearchParamsModel, Query()],
) -> ServiceFilmSearchParamsModel:
    return ServiceFilmSearchParamsModel.model_validate(request_params.model_dump())


def get_person_search_service_params(
    request_params: Annotated[ApiPersonSearchParamsModel, Query()],
) -> ServicePersonSearchParamsModel:
    return ServicePersonSearchParamsModel.model_validate(request_params.model_dump())


def decode_token(token: str) -> dict[str, Any] | None:
    """
    Функция декодирует токен, используя секретный ключ, сохранённый в объекте settings в поле jwt_secret_key.
    Возвращает содержимое токена в виде словаря или None, если токен невалиден или при декодировании
    было выброшено исключение.
    """
    try:
        algorithms = [
            jwt.get_unverified_header(token)["alg"],
        ]
        return jwt.decode(token, settings.authjwt_secret_key, algorithms=algorithms)
    except Exception:
        return None


@lru_cache()
def get_security_jwt() -> HTTPBearer:
    return HTTPBearer()


async def get_auth_credentials(
    request: Request, bearer: HTTPBearer = Depends(get_security_jwt)
) -> HTTPAuthorizationCredentials | None:
    return await bearer(request)


def get_user_data(
    credentials: HTTPAuthorizationCredentials | None = Depends(get_auth_credentials),
) -> dict[str, Any]:
    if not credentials:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Invalid authorization code.",
        )
    if credentials.scheme != "Bearer":
        raise HTTPException(
            status_code=http.HTTPStatus.UNAUTHORIZED,
            detail="Only Bearer token might be accepted",
        )
    decoded_token = decode_token(credentials.credentials)
    if not decoded_token:
        raise HTTPException(
            status_code=http.HTTPStatus.FORBIDDEN,
            detail="Invalid or expired token.",
        )
    return decoded_token

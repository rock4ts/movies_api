from typing import Annotated
from functools import lru_cache

from elasticsearch import AsyncElasticsearch
import jwt
from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError
from redis.asyncio import Redis

from app.core.config import settings, jwt_settings
from app.core.enums import AccessLabel
from app.db.clients import es, redis
from app.api.v1.request_models import (
    AccessTokenPayload,
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
from .exceptions import CredentialsHttpException

ALL_ACCESS_LABELS = list(AccessLabel)
security_jwt = HTTPBearer(auto_error=False)

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
    return FilmService(redis, elastic, settings.film_index, cache_ttl=settings.cache_ttl)


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic, settings.genre_index, settings.cache_ttl)


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(
        redis,
        elastic,
        settings.person_index,
        settings.film_index,
        settings.cache_ttl,
    )


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


def get_access_token_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_jwt)],
) -> AccessTokenPayload | None:
    if not credentials:
        return None
    try:
        payload = jwt.decode(
            credentials.credentials,
            jwt_settings.public_key,
            algorithms=[jwt_settings.algorithm],
        )
    except jwt.ExpiredSignatureError:
        raise CredentialsHttpException("Token has expired")
    except jwt.InvalidTokenError:
        raise CredentialsHttpException("Invalid token")

    try:
        payload = AccessTokenPayload.model_validate(payload)
    except ValidationError:
        raise CredentialsHttpException("Invalid token payload")

    if payload.type != "access":
        raise CredentialsHttpException("Token is not an access token")

    return payload


def user_access_labels(
    token_payload: Annotated[
        AccessTokenPayload | None,
        Depends(get_access_token_payload),
    ],
) -> list[AccessLabel]:

    if not token_payload:
        return [AccessLabel.FREE]

    if token_payload.is_superuser:
        return ALL_ACCESS_LABELS

    if token_payload.access_labels:
        return token_payload.access_labels

    return [AccessLabel.FREE]

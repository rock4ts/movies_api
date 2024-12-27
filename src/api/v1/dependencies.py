import http
from functools import lru_cache

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis

from core.config import settings
from db.elastic import get_elastic
from db.redis import get_redis
from db.repository import AsyncElasticRepository, AsyncRedisRepository
from services.film import FilmService
from services.genre import GenreService
from services.person import PersonService

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5
GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticRepository = Depends(get_elastic),
) -> FilmService:
    redis_repo = AsyncRedisRepository(redis, FILM_CACHE_EXPIRE_IN_SECONDS)
    elastic_repo = AsyncElasticRepository(elastic, "movies")

    return FilmService(redis_repo, elastic_repo)


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticRepository = Depends(get_elastic),
) -> GenreService:
    redis_repo = AsyncRedisRepository(redis, GENRE_CACHE_EXPIRE_IN_SECONDS)
    elastic_repo = AsyncElasticRepository(elastic, "genres")

    return GenreService(redis_repo, elastic_repo)


@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticRepository = Depends(get_elastic),
) -> PersonService:
    redis_repo = AsyncRedisRepository(redis, GENRE_CACHE_EXPIRE_IN_SECONDS)
    elastic_repo = AsyncElasticRepository(elastic, "persons")

    return PersonService(redis_repo, elastic_repo)


def decode_token(token: str) -> dict | None:
    """
    Функция декодирует токен, используя секретный ключ, сохранённый в объекте settings в поле jwt_secret_key.
    Возвращает содержимое токена в виде словаря или None, если токен невалиден или при декодировании
    было выброшено исключение.
    """
    try:
        return jwt.decode(
            token,
            settings.authjwt_secret_key,
            algorithms=[settings.authjwt_algorithm],
        )
    except Exception:
        return None


class JWTBearer(HTTPBearer):
    """
    Класс - наследник fastapi.security.HTTPBearer. Рекомендуем исследовать этот класс.
    Метод `__call__` класса HTTPBearer возвращает объект HTTPAuthorizationCredentials из заголовка `Authorization`

    class HTTPAuthorizationCredentials(BaseModel):
        scheme: str #  'Bearer'
        credentials: str #  сам токен в кодировке Base64

    FastAPI при использовании класса HTTPBearer добавит всё необходимое для авторизации в Swagger документацию.
    """  # noqa: E501

    def __init__(self, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(
            request
        )
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
        decoded_token = self.parse_token(credentials.credentials)
        if not decoded_token:
            raise HTTPException(
                status_code=http.HTTPStatus.FORBIDDEN,
                detail="Invalid or expired token.",
            )
        return decoded_token

    @staticmethod
    def parse_token(jwt_token: str) -> dict | None:
        return decode_token(jwt_token)


security_jwt = JWTBearer()

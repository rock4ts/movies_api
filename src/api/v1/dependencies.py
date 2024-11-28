from functools import lru_cache

from fastapi import Depends
from redis.asyncio import Redis

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
    elastic: AsyncElasticRepository = Depends(get_elastic)
) -> FilmService:
    redis_repo = AsyncRedisRepository(redis, FILM_CACHE_EXPIRE_IN_SECONDS)
    elastic_repo = AsyncElasticRepository(elastic, 'movies')

    return FilmService(redis_repo, elastic_repo)


@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticRepository = Depends(get_elastic),
) -> GenreService:
    redis_repo = AsyncRedisRepository(redis, GENRE_CACHE_EXPIRE_IN_SECONDS)
    elastic_repo = AsyncElasticRepository(elastic, 'genres')

    return GenreService(redis_repo, elastic_repo)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticRepository = Depends(get_elastic),
) -> PersonService:
    redis_repo = AsyncRedisRepository(redis, GENRE_CACHE_EXPIRE_IN_SECONDS)
    elastic_repo = AsyncElasticRepository(elastic, 'persons')

    return PersonService(redis_repo, elastic_repo)

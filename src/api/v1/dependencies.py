from functools import lru_cache

from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from db.repository import AsyncRedisRepository, AsyncElasticRepository
from services.film import FilmService

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


@lru_cache()
def get_film_service(redis: Redis = Depends(get_redis),
                     elastic: AsyncElasticRepository = Depends(get_elastic)
                     ) -> FilmService:
    redis_repo = AsyncRedisRepository(redis, FILM_CACHE_EXPIRE_IN_SECONDS)
    elastic_repo = AsyncElasticRepository(elastic, 'movies')

    return FilmService(redis_repo, elastic_repo)

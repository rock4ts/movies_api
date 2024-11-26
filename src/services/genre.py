import logging

from pydantic import UUID4

from db.repository import AsyncElasticRepository, AsyncRedisRepository
from models.genre import Genre, GenreList

from .base import BaseService
from .schemas import GenresElasticParams

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService(BaseService):

    logger = logging.getLogger(__name__)

    def __init__(self,
                 _redis_repo: AsyncRedisRepository,
                 _elastic_repo: AsyncElasticRepository):
        self._redis_repo = _redis_repo
        self._elastic_repo = _elastic_repo

# для эндпоинта /genres
    async def get_genres(self) -> GenreList|None:
        redis_key = self._create_redis_key(
            self._elastic_repo.index
        )
        genres_list = await self._redis_repo.get(redis_key, GenreList)
        if not genres_list:
            self.logger.info("Could not find cached genres by '%s'", redis_key)
            search_params = self._create_elastic_search_params()
            genres_list = await self._elastic_repo.list(search_params, GenreList)
            if not genres_list.items:
                self.logger.info("Could not find genres by params '%s'", redis_key)
                return genres_list

            await self._redis_repo.save(redis_key, genres_list)

        return genres_list

    def _create_elastic_search_params(
        self
    ) -> GenresElasticParams:
        search_params = GenresElasticParams(
            musts=[], from_=0, size=50
        )
        return search_params

# для эндпоинта /genres/{genre_id}
    async def get_genre_by_id(
        self,
        genre_id: UUID4
    ) -> Genre|None:
        redis_key = self._create_redis_key(self._elastic_repo.index, [genre_id])
        genre = await self._redis_repo.get(redis_key, Genre)
        if not genre:
            self.logger.info("Could not find cached genre by '%s'", redis_key)
            genre = await self._elastic_repo.get(genre_id, Genre)
            if not genre:
                self.logger.info("Could not find genre '%s'", genre_id)
                return None
            await self._redis_repo.save(redis_key, genre)

        return genre

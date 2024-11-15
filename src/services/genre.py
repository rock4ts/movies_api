from functools import lru_cache
import logging
from typing import List, Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.genre import Genre, GenreList

logger = logging.getLogger(__name__)

CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

# для эндпоинта /genres
    async def get_all(self) -> Optional[List[Genre]]:
        genres: Optional[GenreList] = await self._genres_from_cache()
        if not genres:
            genres: List[Genre] = await self._get_genres_from_elastic()
            if not genres:
                logger.error('Elasticsearch. Not found')
                return None
            await self._put_genres_to_cache(genres)
            genres = GenreList(genres=genres)
        return genres.genres

    async def _get_genres_from_elastic(self) -> List[Genre]:
        try:
            docs = await self.elastic.search(
                index='genres',
                query={"match_all": {}},
                size=20,
            )
        except NotFoundError:
            return None

        hits: List[dict] = docs['hits']['hits']
        genres_list = [Genre(**hit['_source']) for hit in hits]
        return genres_list

    async def _genres_from_cache(self) -> Optional[GenreList]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data: List[Genre] = await self.redis.get("genres")
        if not data:
            return None

        return GenreList.model_validate_json(data)

    async def _put_genres_to_cache(self, genres: List[Genre]):
        # Сохраняем данные о жанрах, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        genre_list = GenreList(genres=genres)
        await self.redis.set(
            "genres", genre_list.model_dump_json(), CACHE_EXPIRE_IN_SECONDS
        )

# для эндпоинта /genres/{uuid}
    async def get_by_id(self, uuid: str) -> Optional[Genre]:
        genre = await self._genre_from_cache(uuid)
        if not genre:
            genre = await self._get_genre_from_elastic(uuid)
            if not genre:
                logger.error('Elasticsearch. Not found')
                return None
            await self._put_genre_to_cache(genre)

        return genre

    async def _get_genre_from_elastic(self, uuid: str) -> Optional[Genre]:
        try:
            doc = await self.elastic.get(index='genres', id=uuid)
        except NotFoundError:
            return None
        return Genre(**doc['_source'])

    async def _genre_from_cache(self, uuid: str) -> Optional[Genre]:
        # Пытаемся получить данные о фильме из кеша, используя команду get
        # https://redis.io/commands/get/
        data = await self.redis.get(uuid)
        if not data:
            return None

        return Genre.model_validate_json(data)

    async def _put_genre_to_cache(self, genre: Genre):
        # Сохраняем данные о фильме, используя команду set
        # Выставляем время жизни кеша — 5 минут
        # https://redis.io/commands/set/
        # pydantic позволяет сериализовать модель в json
        await self.redis.set(
            str(genre.uuid), genre.model_dump_json(), CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)

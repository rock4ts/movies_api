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

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


# FilmService содержит бизнес-логику по работе с фильмами.
# Никакой магии тут нет. Обычный класс с обычными методами.
# Этот класс ничего не знает про DI — максимально сильный и независимый.
class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_all возвращает список объектов. Он опционален, так как жанры могут отсутствовать в базе
    async def get_all(self) -> Optional[List[Genre]]:
        logger.debug('Пытаемся получить данные из кеша')
        genres: Optional[GenreList] = await self._genres_from_cache()
        if not genres:
            logger.debug('Если фильма нет в кеше, то ищем его в Elasticsearch')
            genres: List[Genre] = await self._get_genres_from_elastic()
            if not genres:
                logger.error('Если он отсутствует в Elasticsearch, значит жанров вообще нет в базе')
                return None
            logger.debug('Сохраняем фильм в кеш')
            await self._put_genres_to_cache(genres)
            genres = GenreList(genres=genres)
        return genres.genres

    async def _get_genres_from_elastic(self) -> Optional[GenreList]:
        try:
            docs = await self.elastic.search(
                index='genres',
                query={"match_all": {}},
                size=20,
            )
        except NotFoundError:
            return None
        logger.debug('get_genres_from_elastic = sucess')

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
        await self.redis.set("genres", genre_list.model_dump_json(by_alias=True), FILM_CACHE_EXPIRE_IN_SECONDS)


# get_genres_service — это провайдер FilmService. 
# С помощью Depends он сообщает, что ему необходимы Redis и Elasticsearch
# Для их получения вы ранее создали функции-провайдеры в модуле db
# Используем lru_cache-декоратор, чтобы создать объект сервиса в едином экземпляре (синглтона)
@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)

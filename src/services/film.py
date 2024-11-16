from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from redis.asyncio import Redis

from models.film import Film, FilmDetail
from .schemas import ElasticSearchParams

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_films(self, search_params: ElasticSearchParams) -> list[Film]:
        films = await self._get_films_from_elastic(search_params)

        return films

    async def _get_films_from_elastic(self, search_params: ElasticSearchParams) -> list[Film]:
        body = {
            "query": {
                "bool": {
                    "filter": search_params.filters,
                    "must": search_params.musts,
                }
            },
            "sort": search_params.sorts,
            "from": search_params.from_,
            "size": search_params.size,
        }

        response = await self.elastic.search(index='movies', body=body)
        films = [Film(**doc['_source']) for doc in response['hits']['hits']]

        return films

    # TODO
    async def get_film_by_id(self, film_id: str) -> Optional[FilmDetail]:
        # film = await self._film_from_cache(film_id)
        # if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            # await self._put_film_to_cache(film)

            return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[FilmDetail]:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None

        return FilmDetail(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[FilmDetail]:
        data = await self.redis.get(film_id)
        if not data:
            return None
        film = Film.model_validate_json(data)

        return film

    async def _put_film_to_cache(self, film: FilmDetail):
        await self.redis.set(
            film.uuid,
            film.model_dump_json(),
            FILM_CACHE_EXPIRE_IN_SECONDS
            )

import logging
from typing import Any

from elasticsearch import NotFoundError
from pydantic import UUID4

from .base import BaseService
from .schemas import FilmListParamsDTO, FilmSearchParamsDTO


class FilmService(BaseService):
    logger: logging.Logger = logging.getLogger(__name__)

    @staticmethod
    def _apply_pagination(
        body: dict[str, Any], page_number: int | None, page_size: int | None
    ) -> None:
        if page_size and page_number:
            body["from"] = (page_number - 1) * page_size
            body["size"] = page_size

    def _get_film_list_cache_key(self, film_list_params: FilmListParamsDTO) -> str:
        return (
            f"{self._index}:{film_list_params.sort}:{film_list_params.genre_id}:"
            f"{film_list_params.page_number}:{film_list_params.page_size}"
        )

    def _get_film_detail_cache_key(self, film_id: UUID4) -> str:
        return f"{self._index}:{film_id}"

    def _get_film_search_cache_key(self, film_search_params: FilmSearchParamsDTO) -> str:
        return (
            f"{self._index}:{film_search_params.query}:"
            f"{film_search_params.page_number}:{film_search_params.page_size}"
        )

    def _prepare_film_list_es_body(self, film_list_params: FilmListParamsDTO) -> dict[str, Any]:
        body: dict[str, Any] = {
            "query": {
                "bool": {
                    "filter": [],
                    "must": [],
                }
            },
        }
        if film_list_params.genre_id:
            body["query"]["bool"]["filter"].append(
                {
                    "nested": {
                        "path": "genres",
                        "query": {
                            "bool": {
                                "must": [{"term": {"genres.id": str(film_list_params.genre_id)}}]
                            }
                        },
                    }
                }
            )
        self._apply_pagination(body, film_list_params.page_number, film_list_params.page_size)
        if film_list_params.sort:
            body["sort"] = [
                {"imdb_rating": {"order": "desc" if film_list_params.sort.startswith("-") else "asc"}}
            ]
        return body

    def _prepare_film_search_es_body(
        self, film_search_params: FilmSearchParamsDTO
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "query": {
                "bool": {
                    "filter": [],
                    "must": [],
                }
            },
        }
        if film_search_params.query:
            body["query"]["bool"]["must"].append({"match": {"title": film_search_params.query}})
        self._apply_pagination(body, film_search_params.page_number, film_search_params.page_size)
        return body

    async def _get_films(
        self, es_request_body: dict[str, Any], cache_key: str
    ) -> list[dict[str, Any]]:
        film_list: list[dict[str, str]] | None = None
        film_list = await self._cache_get(cache_key)
        if film_list:
            return film_list

        self.logger.info(f"Could not find cached films by {cache_key}")
        response = await self._elastic.search(index=self._index, body=es_request_body)
        film_list = [film["_source"] for film in response["hits"]["hits"]]
        if not film_list:
            self.logger.info(f"Elasticsearch could not find films by {es_request_body}")
            return []
        await self._cache_set(cache_key, film_list)
        return film_list

    async def list_films(self, film_list_params: FilmListParamsDTO) -> list[dict[str, Any]]:
        cache_key = self._get_film_list_cache_key(film_list_params)
        es_request_body = self._prepare_film_list_es_body(film_list_params)
        return await self._get_films(es_request_body, cache_key)

    async def search_films(self, film_search_params: FilmSearchParamsDTO) -> list[dict[str, Any]]:
        cache_key = self._get_film_search_cache_key(film_search_params)
        es_request_body = self._prepare_film_search_es_body(film_search_params)
        return await self._get_films(es_request_body, cache_key)

    async def get_film_by_id(self, film_id: UUID4) -> dict[str, str] | None:
        cache_key = self._get_film_detail_cache_key(film_id)
        cached_film = await self._cache_get(cache_key)
        if cached_film:
            return cached_film

        self.logger.info(f"Could not find cached film by {cache_key}")
        try:
            response = await self._elastic.get(index=self._index, id=str(film_id))
        except NotFoundError:
            self.logger.info(f"Could not find film {film_id}")
            return None

        film = response["_source"]
        await self._cache_set(cache_key, film)
        return film

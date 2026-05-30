import logging
from typing import Any

from elasticsearch import NotFoundError
from pydantic import UUID4

from .base import BaseService


class GenreService(BaseService):
    logger: logging.Logger = logging.getLogger(__name__)

    def _get_genre_list_cache_key(self) -> str:
        return self._index

    def _get_genre_detail_cache_key(self, genre_id: UUID4) -> str:
        return f"{self._index}:{genre_id}"

    async def get_genres(self) -> list[dict[str, str]]:
        cache_key = self._get_genre_list_cache_key()
        genres = await self._cache_get(cache_key)
        if genres:
            return genres

        self.logger.info(f"Could not find cached genres by {cache_key}")
        response = await self._elastic.search(
            index=self._index,
            body={"query": {"match_all": {}}},
        )
        genres = [genre["_source"] for genre in response["hits"]["hits"]]
        if not genres:
            self.logger.info("Elasticsearch could not find genres")
            return []

        await self._cache_set(cache_key, genres)
        return genres

    async def get_genre_by_id(self, genre_id: UUID4) -> dict[str, Any] | None:
        cache_key = self._get_genre_detail_cache_key(genre_id)
        cached_genre = await self._cache_get(cache_key)
        if cached_genre:
            return cached_genre

        self.logger.info(f"Could not find cached genre by {cache_key}")
        try:
            response = await self._elastic.get(index=self._index, id=str(genre_id))
        except NotFoundError:
            self.logger.info(f"Could not find genre {genre_id}")
            return None

        genre = response["_source"]
        await self._cache_set(cache_key, genre)
        return genre

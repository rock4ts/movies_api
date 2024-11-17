
import logging
from typing import Optional, Union

from pydantic import UUID4

from api.v1.schemas import FilmListParams, FilmSearchParams
from db.repository import AsyncRedisRepository, AsyncElasticRepository
from models.film import FilmDetail, FilmList
from .base import BaseService
from .schemas import ElasticSearchParams


class FilmService(BaseService):

    logger = logging.getLogger(__name__)

    def __init__(self,
                 _redis_repo: AsyncRedisRepository,
                 _elastic_repo: AsyncElasticRepository):
        self._redis_repo = _redis_repo
        self._elastic_repo = _elastic_repo

    async def get_films(self,
                        query_params: Union[FilmListParams | FilmSearchParams]
                        ) -> FilmList:
        redis_key = self._create_redis_key(
            self._elastic_repo.index,
            query_params
            )
        film_list = await self._redis_repo.get(redis_key, FilmList)
        if not film_list:
            self.logger.info(f"Could not find cached films by {redis_key}")
            search_params = self._create_elastic_search_params(query_params)
            film_list = await self._elastic_repo.list(search_params, FilmList)
            if not film_list.items:
                self.logger.info(f"Could not find films by params {redis_key}")
                return film_list

            await self._redis_repo.save(redis_key, film_list)

        return film_list

    async def get_film_by_id(self,
                             film_id: UUID4
                             ) -> Optional[FilmDetail]:
        redis_key = self._create_redis_key(self._elastic_repo.index, [film_id])
        film = await self._redis_repo.get(redis_key, FilmDetail)
        if not film:
            self.logger.info(f"Could not find cached film by {redis_key}")
            film = await self._elastic_repo.get(film_id, FilmDetail)
            if not film:
                self.logger.info(f"Could not find film {film_id}")
                return None
            await self._redis_repo.save(redis_key, film)

        return film

    # TODO потенциально и это можно вынести в BaseService
    def _create_elastic_search_params(
        self,
        query_params: Union[FilmListParams | FilmSearchParams]
        ) -> ElasticSearchParams:
        search_params = ElasticSearchParams()

        if query_params.pagination_params:
            search_params.from_ = (
                query_params.pagination_params.page_number - 1
                ) * query_params.pagination_params.page_size
            search_params.size = query_params.pagination_params.page_size

        if query_params.sort:
            sort_field = query_params.sort.lstrip('-')
            sort_order = "desc" if query_params.sort.startswith('-') else "asc"
            search_params.sorts.append({sort_field: {"order": sort_order}})

        if query_params.genre_id:
            search_params.filters.append({
                "nested": {
                    "path": "genres",
                    "query": {"bool": {
                        "must": [{ "term": {"genres.id": query_params.genre_id}}]
                        }
                    }
                }
            })
        if isinstance(query_params, FilmSearchParams) and query_params.query:
            search_params.musts.append(
                {"match": {"title": {"query": query_params.query}}}
                )

        return search_params


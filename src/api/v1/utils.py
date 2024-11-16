

from typing import Union

from api.v1.schemas import FilmListParams, FilmSearchParams
from services.schemas import ElasticSearchParams


async def create_film_search_params(
        query_params: Union[FilmListParams | FilmSearchParams]
        ) -> ElasticSearchParams:
    search_params = ElasticSearchParams(
        sorts=[], filters=[], musts=[], from_=0, size=50
        )

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

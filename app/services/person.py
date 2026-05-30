import logging
from typing import Any

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import UUID4
from redis.asyncio import Redis

from app.api.v1.request_models import PersonSearchParamsModel
from app.core.config import settings

from .base import BaseService


class PersonService(BaseService):
    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(
        self,
        redis: Redis,
        elastic: AsyncElasticsearch,
        index: str,
        film_index: str = settings.film_index,
    ):
        super().__init__(redis, elastic, index)
        self._film_index: str = film_index

    @staticmethod
    def _apply_pagination(
        body: dict[str, Any], page_number: int | None, page_size: int | None
    ) -> None:
        if page_size and page_number:
            body["from"] = (page_number - 1) * page_size
            body["size"] = page_size

    def _get_person_search_cache_key(self, request_params: PersonSearchParamsModel) -> str:
        return (
            f"{self._index}:{request_params.query}:"
            f"{request_params.page_number}:{request_params.page_size}"
        )

    def _get_person_detail_cache_key(self, person_id: UUID4) -> str:
        return f"{self._index}:{person_id}"

    def _get_person_films_cache_key(self, person_id: UUID4) -> str:
        return f"{self._index}:films:{person_id}"

    def _prepare_person_search_es_body(
        self, request_params: PersonSearchParamsModel
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "query": {
                "bool": {
                    "filter": [],
                    "must": [],
                }
            }
        }
        if request_params.query:
            body["query"]["bool"]["must"].append({"match": {"full_name": request_params.query}})
        self._apply_pagination(body, request_params.page_number, request_params.page_size)
        return body

    @staticmethod
    def _prepare_person_films_es_body(person_id: UUID4 | str) -> dict[str, Any]:
        person_id_str = str(person_id)
        return {
            "size": 1000,
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"term": {"directors.id": person_id_str}},
                            }
                        },
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"term": {"actors.id": person_id_str}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"term": {"writers.id": person_id_str}},
                            }
                        },
                    ],
                    "minimum_should_match": 1,
                }
            },
        }

    @staticmethod
    def _prepare_person_films_batch_es_body(person_ids: list[str]) -> dict[str, Any]:
        return {
            "size": 1000,
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "directors",
                                "query": {"terms": {"directors.id": person_ids}},
                            }
                        },
                        {
                            "nested": {
                                "path": "actors",
                                "query": {"terms": {"actors.id": person_ids}},
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {"terms": {"writers.id": person_ids}},
                            }
                        },
                    ],
                    "minimum_should_match": 1,
                }
            },
        }

    async def _search_films_by_person(self, person_id: UUID4 | str) -> list[dict[str, Any]]:
        body = self._prepare_person_films_es_body(person_id)
        response = await self._elastic.search(index=self._film_index, body=body)
        return [film["_source"] for film in response["hits"]["hits"]]

    async def _search_films_by_person_ids(self, person_ids: list[str]) -> list[dict[str, Any]]:
        if not person_ids:
            return []
        body = self._prepare_person_films_batch_es_body(person_ids)
        response = await self._elastic.search(index=self._film_index, body=body)
        return [film["_source"] for film in response["hits"]["hits"]]

    @staticmethod
    def _extract_person_film_roles(
        person_id: UUID4 | str, films: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        person_id_str = str(person_id)
        film_roles: list[dict[str, Any]] = []
        for film in films:
            roles: list[str] = []
            if any(actor["id"] == person_id_str for actor in film.get("actors", [])):
                roles.append("actor")
            if any(writer["id"] == person_id_str for writer in film.get("writers", [])):
                roles.append("writer")
            if any(director["id"] == person_id_str for director in film.get("directors", [])):
                roles.append("director")
            if roles:
                film_roles.append({"id": film["id"], "roles": roles})
        return film_roles

    async def _enrich_person_with_films(self, person: dict[str, Any]) -> dict[str, Any]:
        person_id = person.get("id")
        if not person_id:
            return person

        films = await self._search_films_by_person(person_id)
        person["films"] = self._extract_person_film_roles(person_id, films)
        return person

    @staticmethod
    def _map_film_roles_by_person(
        person_ids: list[str], films: list[dict[str, Any]]
    ) -> dict[str, list[dict[str, Any]]]:
        roles_by_person: dict[str, list[dict[str, Any]]] = {
            person_id: [] for person_id in person_ids
        }
        person_id_set = set(person_ids)

        for film in films:
            film_id = film.get("id")
            if not film_id:
                continue

            roles_per_person: dict[str, list[str]] = {}
            for actor in film.get("actors", []):
                actor_id = actor.get("id")
                if actor_id in person_id_set:
                    roles_per_person.setdefault(actor_id, []).append("actor")
            for writer in film.get("writers", []):
                writer_id = writer.get("id")
                if writer_id in person_id_set:
                    roles_per_person.setdefault(writer_id, []).append("writer")
            for director in film.get("directors", []):
                director_id = director.get("id")
                if director_id in person_id_set:
                    roles_per_person.setdefault(director_id, []).append("director")

            for person_id, roles in roles_per_person.items():
                roles_by_person[person_id].append({"id": film_id, "roles": roles})

        return roles_by_person

    async def search_persons(self, request_params: PersonSearchParamsModel) -> list[dict[str, Any]]:
        cache_key = self._get_person_search_cache_key(request_params)
        cached_persons = await self._cache_get(cache_key)
        if cached_persons:
            return cached_persons

        self.logger.info(f"Could not find cached persons by {cache_key}")
        es_request_body = self._prepare_person_search_es_body(request_params)
        response = await self._elastic.search(index=self._index, body=es_request_body)
        persons = [person["_source"] for person in response["hits"]["hits"]]
        if not persons:
            self.logger.info(f"Elasticsearch could not find persons by {es_request_body}")
            return []

        person_ids = [str(person_id) for person in persons if (person_id := person.get("id"))]
        films = await self._search_films_by_person_ids(person_ids)
        roles_by_person = self._map_film_roles_by_person(person_ids, films)

        enriched_persons: list[dict[str, Any]] = []
        for person in persons:
            person_id = str(person.get("id") or person.get("uuid") or "")
            person["films"] = roles_by_person.get(person_id, [])
            enriched_persons.append(person)

        await self._cache_set(cache_key, enriched_persons)
        return enriched_persons

    async def get_films_by_person(self, person_id: UUID4) -> list[dict[str, Any]]:
        cache_key = self._get_person_films_cache_key(person_id)
        cached_films = await self._cache_get(cache_key)
        if cached_films:
            return cached_films

        self.logger.info(f"Could not find cached films by {cache_key}")
        films = await self._search_films_by_person(person_id)
        if not films:
            self.logger.info(f"Elasticsearch could not find films by person {person_id}")
            return []

        await self._cache_set(cache_key, films)
        return films

    async def get_person_by_id(self, person_id: UUID4) -> dict[str, Any] | None:
        cache_key = self._get_person_detail_cache_key(person_id)
        cached_person = await self._cache_get(cache_key)
        if cached_person:
            return cached_person

        self.logger.info(f"Could not find cached person by {cache_key}")
        try:
            response = await self._elastic.get(index=self._index, id=str(person_id))
        except NotFoundError:
            self.logger.info(f"Could not find person {person_id}")
            return None

        person = await self._enrich_person_with_films(response["_source"])
        await self._cache_set(cache_key, person)
        return person

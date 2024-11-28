from typing import Union

from elasticsearch import NotFoundError

from api.v1.schemas import PersonListParams, PersonSearchParams
from db.repository import AsyncElasticRepository, AsyncRedisRepository
from models.film import FilmList
from models.person import Person, PersonFilmList, PersonList
from services.base import BaseService
from services.schemas import ElasticSearchParams, PersonElasticParams

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService(BaseService):
    def __init__(self,
                 _redis_repo: AsyncRedisRepository,
                 _elastic_repo: AsyncElasticRepository):
        self._redis_repo = _redis_repo
        self._elastic_repo = _elastic_repo

    async def get_persons(
        self, query_params: PersonSearchParams
    ) -> PersonList:
        redis_key = self._create_redis_key('persons', query_params)
        person_list = await self._redis_repo.get(redis_key, PersonList)
        if not person_list:
            search_params = self._create_person_search_params(query_params)
            person_list = await self._get_persons_from_elastic(search_params)
            if not person_list.items:
                return person_list
            await self._redis_repo.save(redis_key, person_list)
        return person_list

    async def get_films_by_person(self, person_uuid: str) -> FilmList:
        redis_key = self._create_redis_key('persons:films', [person_uuid])
        films = await self._redis_repo.get(redis_key, FilmList)
        if not films:
            films = await self._get_films_by_person_from_elastic(person_uuid)
            if not films:
                return None
            await self._redis_repo.save(redis_key, films)
        return films

    async def get_person_by_id(self, person_uuid: str) -> Person|None:
        redis_key = self._create_redis_key('persons', [person_uuid])
        person = await self._redis_repo.get(redis_key, Person)
        if not person:
            person = await self._get_person_from_elastic(person_uuid)
            if not person:
                return None
            await self._redis_repo.save(redis_key, person)
        return person

    async def _get_person_from_elastic(
        self, person_uuid: str
    ) -> Person|None:
        try:
            person = await self._elastic_repo.get(person_uuid, Person)
            films = await self._get_film_roles_by_person(person_uuid)
            person.films = films
        except NotFoundError:
            return None
        return person

    async def _get_persons_from_elastic(
        self, search_params: PersonElasticParams
    ) -> PersonList:
        persons = await self._elastic_repo.list(search_params, PersonList)
        for person in persons.items:
            person_uuid = person.uuid
            films = await self._get_film_roles_by_person(person_uuid)
            person.films = films
        return persons

    async def _get_films_by_person_from_elastic(
            self,
            person_uuid: str
    ) -> FilmList:
        films = await self._search_films_by_person(person_uuid)
        return FilmList(items=films)

    async def _search_films_by_person(self, person_uuid: str) -> list:
        films_query = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "nested": {
                                "path": "directors",
                                "query": {
                                    "term": {
                                        "directors.id": person_uuid
                                    }
                                }
                            }
                        },
                        {
                            "nested": {
                                "path": "actors",
                                "query": {
                                    "term": {
                                        "actors.id": person_uuid
                                    }
                                }
                            }
                        },
                        {
                            "nested": {
                                "path": "writers",
                                "query": {
                                    "term": {
                                        "writers.id": person_uuid
                                    }
                                }
                            }
                        }
                    ],
                "minimum_should_match": 1
                }
            }
        }
        films_response = await self._elastic_repo._elastic.search(
            index="movies", body=films_query
        )
        films = [film['_source'] for film in films_response['hits']['hits']]
        return films

    async def _get_film_roles_by_person(self, person_uuid: str):
        film_roles = []
        films = await self._search_films_by_person(person_uuid)
        for film in films:
            roles = []
            if any(actor['id'] == str(person_uuid) for actor in film.get('actors', [])):
                roles.append("actor")
            if any(writer['id'] == str(person_uuid) for writer in film.get('writers', [])):
                roles.append("writer")
            if any(director['id'] == str(person_uuid) for director in film.get('directors', [])):
                roles.append("director")
            if roles:
                film_roles.append(PersonFilmList(id=film['id'], roles=roles))
        return film_roles

    def _create_person_search_params(
        self,
        query_params: Union[PersonListParams | PersonSearchParams]
    ) -> PersonElasticParams:
        search_params = ElasticSearchParams()

        if query_params.pagination_params:
            search_params.from_ = (
                query_params.pagination_params.page_number - 1
            ) * query_params.pagination_params.page_size
            search_params.size = query_params.pagination_params.page_size

        if isinstance(query_params, PersonSearchParams) and query_params.query:
            search_params.musts.append(
                {"match": {"full_name": {"query": query_params.query}}}
            )
        return search_params

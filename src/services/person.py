from functools import lru_cache
from typing import List, Optional, Union

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from api.v1.schemas import PersonListParams, PersonSearchParams
from db.elastic import get_elastic
from db.redis import get_redis
from models.film import Film, FilmDetail
from models.person import Person, PersonFilmList
from services.schemas import PersonElasticParams

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self,  redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_persons(self, query_params: PersonSearchParams) -> List[Person]:
        search_params = self._create_person_search_params(query_params)
        persons = await self._get_persons_from_elastic(search_params)
        return persons

    async def get_films_by_person(self, person_uuid: str) -> List[Film]:
        # films = await self._films_by_person_from_cache(person_id) # TODO исправить эту и след строчки после реализации кэша
        films = None
        if not films:
            films = await self._get_films_by_person_from_elastic(person_uuid)
            if not films:
                return None
            # await self._put_films_by_person_to_cache(person_uuid, films)
        return films

    async def get_person_by_id(self, person_uuid: str) -> Optional[Person]:
        # person = await self._person_from_cache(person_id) # TODO исправить эту и след строчки после реализации кэша
        person = None
        if not person:
            person = await self._get_person_from_elastic(person_uuid)
            if not person:
                return None
            # await self._put_person_to_cache(person)
        return person

    async def _get_person_from_elastic(self, person_uuid: str) -> Optional[Person]:
        try:
            person = await self.elastic.get(index='persons', id=person_uuid)
            films = await self._get_film_roles_by_person(person_uuid)
            person['_source']['films'] = films
        except NotFoundError:
            return None
        return Person(**person['_source'])

    async def _get_persons_from_elastic(self, search_params: PersonElasticParams) -> List[Person]:
        body = {
            "query": {
                "bool": {
                    "must": search_params.musts,
                }
            },
            "from": search_params.from_,
            "size": search_params.size,
        }
        persons_response = await self.elastic.search(index='persons', body=body)
        for person in persons_response.body['hits']['hits']:
            person_uuid = person['_id']
            films = await self._get_film_roles_by_person(person_uuid)
            person['_source']['films'] = films

        return [Person(**person['_source']) for person in persons_response.body['hits']['hits']]

    async def _get_films_by_person_from_elastic(self, person_uuid: str) -> Optional[PersonFilmList]:
        try:
            films = await self._search_films_by_person(person_uuid)
        except NotFoundError:
            return None
        return films

    async def _search_films_by_person(self, person_uuid: str) -> List:
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
                    ]
                }
            }
        }
        films_response = await self.elastic.search(index="movies", body=films_query)
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

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(person.id, person.json(), PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def _films_by_person_from_cache(self, person_uuid: str) -> Optional[Person]:
        data = await self.redis.get(f'{person_uuid}/films')
        if not data:
            return None
        # TODO json magic
        return data

    async def _put_films_by_person_to_cache(self, person_uuid: str, films: [Film]):
        await self.redis.set(f'{person_uuid}/films', films.json(), PERSON_CACHE_EXPIRE_IN_SECONDS)

    def _create_person_search_params(
    self,
    query_params: Union[PersonListParams | PersonSearchParams]) -> PersonElasticParams:
        search_params = PersonElasticParams(
            musts=[], from_=0, size=50
            )

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


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)

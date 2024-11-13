from functools import lru_cache
from typing import Optional

from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis
from models.person import Person, PersonFilmList

PersonFilmList

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5

class PersonService:
    def __init__(self,  redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic


    async def get_by_id(self, person_id: str) -> Optional[Person]:
        # person = await self._person_from_cache(person_id) # TODO исправить эту и след строчки после реализации кэша
        person = None
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            # await self._put_person_to_cache(person)
        return person


    async def _get_person_from_elastic(self, person_uuid: str) -> Optional[Person]:
        try:
            person = await self.elastic.get(index='persons', id=person_uuid)
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
            films = []
            for film in films_response['hits']['hits']:
                film_data = film['_source']
                roles = []

                if any(actor['id'] == str(person_uuid) for actor in film_data.get('actors', [])):
                    roles.append("actor")
                if any(writer['id'] == str(person_uuid) for writer in film_data.get('writers', [])):
                    roles.append("writer")
                if any(director['id'] == str(person_uuid) for director in film_data.get('directors', [])):
                    roles.append("director")

                if roles:
                    films.append({'id': film_data['id'], 'roles': roles})
            person['_source']['films'] = films
        except NotFoundError:
            return None
        return Person(**person['_source'])


    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None
        person = Person.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(person.id, person.json(), PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)

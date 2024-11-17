import abc
from typing import Union, Type

from elasticsearch import AsyncElasticsearch, NotFoundError
from pydantic import BaseModel, UUID4
from redis.asyncio import Redis

from models.base import Item, ItemList
from services.schemas import ElasticSearchParams


class AsyncAbstractRepository(abc.ABC):

    @abc.abstractmethod
    async def get(self, *args, **kwargs) -> BaseModel:
        raise NotImplementedError

    async def list(self, *args, **kwargs) -> BaseModel:
        raise NotImplementedError

    async def save(self, *args, **kwargs):
        raise NotImplementedError


class AsyncElasticRepository(AsyncAbstractRepository):
    def __init__(self, elastic: AsyncElasticsearch, index: str):
        self._elastic = elastic
        self.index = index

    async def get(self, id: UUID4, model: Type[Item]) -> Item:
        try:
            doc = await self._elastic.get(index=self.index, id=id)
        except NotFoundError:
            return None

        return model(**doc['_source'])

    async def list(self,
                   search_params: ElasticSearchParams,
                   model: Type[ItemList]
                   ) -> ItemList:
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
        response = await self._elastic.search(index=self.index, body=body)
        docs = [hit["_source"] for hit in response['hits']['hits']]

        return model(items=docs)


class AsyncRedisRepository(AsyncAbstractRepository):
    def __init__(self, redis: Redis, expires_after: int = 60 * 5):
        self._redis = redis
        self._expires_after = expires_after

    async def get(self,
                  key: str,
                  model: Union[Type[Item], Type[ItemList]]
                  ) -> Union[Item, ItemList, None]:

        json_data = await self._redis.get(key)
        if not json_data:
            return None

        model_data = model.model_validate_json(json_data)
        return model_data

    async def save(self, key: str, model_data: Union[Item, ItemList]):
        await self._redis.set(
            key,
            model_data.model_dump_json(),
            self._expires_after
            )

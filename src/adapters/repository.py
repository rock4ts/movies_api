import abc

from pydantic import BaseModel
from elasticsearch import AsyncElasticsearch


class AsyncAbstractRepository(abc.ABC):
    @abc.abstractmethod
    async def get(self) -> BaseModel:
        raise NotImplementedError

    @abc.abstractmethod
    async def list(self):
        pass


class AsyncElasticRepository(AsyncAbstractRepository):
    def __init__(self, client: AsyncElasticsearch):
        self._client = client

    async def get(self, index, uuid):
        pass

    async def list(self, index, *args, **kwargs):
        pass

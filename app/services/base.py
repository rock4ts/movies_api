import json
import logging
from typing import Any

from redis.asyncio import Redis
from elasticsearch import AsyncElasticsearch


class BaseService:
    logger: logging.Logger = logging.getLogger(__name__)

    def __init__(
        self, redis: Redis, elastic: AsyncElasticsearch, index: str, cache_ttl: int = 300
    ):
        self._index = index
        self._redis = redis
        self._elastic = elastic
        self._cache_ttl = cache_ttl

    async def _cache_get(self, key: str) -> Any | None:
        cached_value = await self._redis.get(key)
        if cached_value is None:
            return None

        if isinstance(cached_value, bytes):
            cached_value = cached_value.decode("utf-8")

        try:
            return json.loads(cached_value)
        except json.JSONDecodeError:
            self.logger.warning("Could not decode cached value for key %s", key)
            return None

    async def _cache_set(self, key: str, value: Any) -> None:
        await self._redis.set(key, json.dumps(value), ex=self._cache_ttl)

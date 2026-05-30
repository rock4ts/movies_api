from elasticsearch import AsyncElasticsearch
from redis.asyncio import Redis

from app.core.config import redis_settings, elastic_settings

redis = Redis(host=redis_settings.host, port=redis_settings.port)
es = AsyncElasticsearch(hosts=[elastic_settings.url])

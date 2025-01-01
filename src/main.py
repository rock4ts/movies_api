"""Entrypoint to app
"""
import logging
from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films, genres, persons
from core.config import settings
from db import elastic, redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis.redis = Redis(
        host=settings.redis_host, port=settings.redis_port
    )
    elastic.es = AsyncElasticsearch(
        hosts=[settings.elastic_url]
    )
    logging.info('Lifespan started')
    yield


app = FastAPI(
    title=settings.project_name,
    root_path='/api',
    default_response_class=ORJSONResponse,
    description="API for cinema",
    lifespan=lifespan
)


app.include_router(films.router, prefix='/v1/films', tags=['films'])
app.include_router(genres.router, prefix='/v1/genres', tags=['genres'])
app.include_router(persons.router, prefix='/v1/persons', tags=['persons'])

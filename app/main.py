"""Entrypoint to app"""

import logging.config

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.v1 import films, genres, persons
from app.core.config import settings
from app.core.logging_setup import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)


app = FastAPI(
    title=settings.project_name,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
    description="API for cinema",
)


app.include_router(films.router, prefix="/api/v1/films", tags=["films"])
app.include_router(genres.router, prefix="/api/v1/genres", tags=["genres"])
app.include_router(persons.router, prefix="/api/v1/persons", tags=["persons"])

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

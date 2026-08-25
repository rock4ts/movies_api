"""Entrypoint to app"""

import logging.config

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.v1 import router as api_v1_router
from app.core.config import sentry_settings, settings
from app.core.logging_setup import LOGGING_CONFIG
from app.core.sentry import configure_sentry

logging.config.dictConfig(LOGGING_CONFIG)
configure_sentry(sentry_settings, service_name="movies-api")


app = FastAPI(
    title=settings.project_name,
    root_path="/movies/api",
    default_response_class=ORJSONResponse,
    description="API for cinema",
)

app.include_router(api_v1_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

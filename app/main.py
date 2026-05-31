"""Entrypoint to app"""

import logging.config

import uvicorn
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.logging_setup import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)


app = FastAPI(
    title=settings.project_name,
    root_path="/api",
    default_response_class=ORJSONResponse,
    description="API for cinema",
)

app.include_router(api_v1_router)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

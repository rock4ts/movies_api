from fastapi import APIRouter
from .genres import router as genres_router
from .persons import router as persons_router
from .films import router as films_router

router = APIRouter(prefix="/v1")
router.include_router(films_router, prefix="/films", tags=["films"])
router.include_router(genres_router, prefix="/genres", tags=["genres"])
router.include_router(persons_router, prefix="/persons", tags=["persons"])

import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from app.services.genre import GenreService

from .dependencies import get_genre_service
from .response_models import Genre

logger = logging.getLogger(__name__)

router = APIRouter()


# для эндпоинта /genres
@router.get(
    "/",
    response_model=list[Genre],
    summary="Список жанров",
)
async def genres(genre_service: GenreService = Depends(get_genre_service)) -> list[dict[str, str]]:
    """
    Эндпоинт для получения списка всех жанров
    """
    return await genre_service.get_genres()


# для эндпоинта /genres/{uuid}
@router.get("/{genre_id}", response_model=Genre, summary="Данные по конкретному жанру")
async def genre_details(
    genre_id: UUID4, genre_service: GenreService = Depends(get_genre_service)
) -> dict[str, str]:
    """
    Детали по жанру
    """
    genre = await genre_service.get_genre_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="genre not found")

    return genre

from typing import List
from fastapi import APIRouter
from pydantic import UUID4
from models.genre import Genre
from models.responses import (
    GenreListResponse, GenreDetailResponse
)

# Объект router, в котором регистрируем обработчики
router = APIRouter()


# Mock для эндпоинта /genres
@router.get(
    "", response_model=List[Genre], summary="Список жанров"
)
async def genres() -> List[Genre]:
    """
    Эндпоинт для получения списка всех жанров
    """
    return GenreListResponse.response       # TODO Заменить Mock на реальный сервис и ответ


# Mock для эндпоинта /genres/{uuid}
@router.get(
    "/{uuid}", response_model=Genre, summary="Данные по конкретному жанру"
)
async def genre_details(uuid: UUID4) -> Genre:
    """
    Детали по жанру
    """
    return GenreDetailResponse.response     # TODO Заменить Mock на реальный сервис и ответ

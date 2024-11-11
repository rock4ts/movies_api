from typing import List, Optional
from fastapi import APIRouter, Query
from pydantic import UUID4
from models.film import Film, FilmDetail
from models.responses import (
    FilmDetailResponse, FilmListResponse, FilmSearchResponse
)

# Объект router, в котором регистрируем обработчики
router = APIRouter()


# Mock для эндпоинта /films
@router.get(
    "", response_model=List[Film], summary="Получить список популярных фильмов"
)
async def films(
    sort: Optional[str] = Query(
        None,
        description="Поле для сортировки, например `-imdb_rating` для сортировки по убыванию рейтинга.",
        example="-imdb_rating"
    ),
    genre: Optional[UUID4] = Query(
        None,
        description="UUID жанра для фильтрации списка фильмов."
    ),
    page_size: int = Query(
        50,
        description="Количество фильмов на странице.",
        ge=1,
        le=100
    ),
    page_number: int = Query(
        1,
        description="Номер страницы.",
        ge=1
    )
) -> List[Film]:
    """
    Эндпоинт для получения списка фильмов 
    с возможностью фильтрации по жанру и сортировке по рейтингу.
    """
    return FilmListResponse.response        # TODO Заменить Mock на реальный сервис и ответ


# Mock для эндпоинта /films/{uuid}
@router.get(
    "/{uuid}", response_model=FilmDetail, summary="Полная информация по фильму"
)
async def film_details(uuid: UUID4) -> FilmDetail:
    """
    Детали фильма
    """
    return FilmDetailResponse.response      # TODO Заменить Mock на реальный сервис и ответ


# Mock для эндпоинта /films/search
@router.get(
    "/search", response_model=List[Film], summary="Поиск по фильмам"
)
async def films_search(query: str) -> List[Film]:
    """
    Эндпоинт для поиска фильмов по ключевым словам.
    """
    return FilmSearchResponse.response      # TODO Заменить Mock на реальный сервис и ответ

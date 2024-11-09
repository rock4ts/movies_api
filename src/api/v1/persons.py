from typing import List
from fastapi import APIRouter
from pydantic import UUID4
from models.film import Film
from models.person import Person
from models.responses import (
    PersonSearchResponse, PersonDetailResponse, PersonFilmListResponse
)

# Объект router, в котором регистрируем обработчики
router = APIRouter()


# Mock для эндпоинта /persons/{uuid}/film
@router.get(
    "", response_model=List[Film], summary="Фильмы по персоне"
)
async def persons_films() -> List[Film]:
    """
    Все фильмы по персоне
    """
    return PersonFilmListResponse.response      # TODO Заменить Mock на реальный сервис и ответ


# Mock для эндпоинта /persons/{uuid}
@router.get(
    "/{uuid}", response_model=Person, summary="Данные по персоне"
)
async def person_details(uuid: UUID4) -> Person:
    """
    Детали по персоне
    """
    return PersonDetailResponse.response        # TODO Заменить Mock на реальный сервис и ответ


# Mock для эндпоинта /persons/search
@router.get(
    "/search", response_model=List[Person], summary="Поиск по персонам"
)
async def person_search(query: str) -> List[Person]:
    """
    Эндпоинт для поиска актеров, режиссеров и сценаристов.
    """
    return PersonSearchResponse.response        # TODO Заменить Mock на реальный сервис и ответ

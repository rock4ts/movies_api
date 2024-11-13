from http import HTTPStatus

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from models.film import Film
from models.person import Person
from models.responses import (
    PersonSearchResponse, PersonDetailResponse, PersonFilmListResponse
)
from services.person import get_person_service, PersonService

router = APIRouter()


@router.get("/{uuid}/film", response_model=List[Film], summary="Фильмы по персоне")
async def persons_films() -> List[Film]:
    """
    Все фильмы по персоне
    """
    return PersonFilmListResponse.response      # TODO Заменить Mock на реальный сервис и ответ


@router.get("/{uuid}", response_model=Person, summary="Данные по персоне")
async def person_details(uuid: UUID4, person_service: PersonService = Depends(get_person_service)) -> Person:
    """
    Детали по персоне
    """
    person = await person_service.get_by_id(uuid)
    print(f'person: {person}')
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return person


@router.get("/search", response_model=List[Person], summary="Поиск по персонам")
async def person_search(query: str) -> List[Person]:
    """
    Эндпоинт для поиска актеров, режиссеров и сценаристов.
    """
    return PersonSearchResponse.response        # TODO Заменить Mock на реальный сервис и ответ

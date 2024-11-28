from http import HTTPStatus

from elasticsearch import NotFoundError
from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from api.v1.dependencies import get_person_service
from api.v1.schemas import PersonSearchParams
from models.film import Film
from models.person import Person
from services.person import PersonService

router = APIRouter()


@router.get("/search", response_model=list[Person], summary="Поиск по персонам")
async def person_search(query_params: PersonSearchParams = Depends(),
                        person_service: PersonService = Depends(get_person_service)) -> list[Person]:
    """
    Эндпоинт для поиска актеров, режиссеров и сценаристов.
    """
    persons = await person_service.get_persons(query_params)
    return persons.items


@router.get("/{uuid}/film", response_model=list[Film], summary="Фильмы по персоне")
async def persons_films(uuid: UUID4,
                        person_service: PersonService = Depends(get_person_service)) -> list[Film]:
    """
    Все фильмы по персоне
    """
    try:
        films = await person_service.get_films_by_person(uuid)
    except NotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return films.items


@router.get("/{uuid}", response_model=Person, summary="Данные по персоне")
async def person_details(uuid: UUID4,
                         person_service: PersonService = Depends(get_person_service)) -> Person:
    """
    Детали по персоне
    """
    person = await person_service.get_person_by_id(uuid)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return person

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import UUID4

from app.api.v1.dependencies import get_person_service
from app.api.v1.request_models import PersonSearchParamsModel
from app.services.person import PersonService

from .response_models import FilmShort, Person

router = APIRouter()


@router.get("/search", response_model=list[Person], summary="Поиск по персонам")
async def person_search(
    request_params: Annotated[PersonSearchParamsModel, Query()],
    person_service: Annotated[PersonService, Depends(get_person_service)],
) -> list[dict[str, str]]:
    """
    Эндпоинт для поиска актеров, режиссеров и сценаристов.
    """
    return await person_service.search_persons(request_params)


@router.get("/{person_id}/film", response_model=list[FilmShort], summary="Фильмы по персоне")
async def persons_films(
    person_id: UUID4,
    person_service: Annotated[PersonService, Depends(get_person_service)],
) -> list[dict[str, str]]:
    """
    Все фильмы по персоне
    """
    return await person_service.get_films_by_person(person_id)


@router.get("/{person_id}", response_model=Person, summary="Данные по персоне")
async def person_details(
    person_id: UUID4,
    person_service: Annotated[PersonService, Depends(get_person_service)],
) -> dict[str, str]:
    """
    Детали по персоне
    """
    person = await person_service.get_person_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="person not found")
    return person

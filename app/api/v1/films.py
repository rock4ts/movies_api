import logging
from http import HTTPStatus
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from app.core.enums import AccessLabel
from app.services.film import FilmAccessError, FilmNotFoundError, FilmService
from app.services.schemas import (
    FilmListParamsDTO as ServiceFilmListParamsModel,
    FilmSearchParamsDTO as ServiceFilmSearchParamsModel,
)

from .dependencies import (
    get_film_list_service_params,
    get_film_search_service_params,
    get_film_service,
    user_access_labels,
)
from .response_models import FilmShort, FilmDetail

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("", response_model=list[FilmShort], summary="Получить список популярных фильмов")
async def films(
    request_params: Annotated[ServiceFilmListParamsModel, Depends(get_film_list_service_params)],
    film_service: Annotated[FilmService, Depends(get_film_service)],
) -> list[dict[str, str]]:
    """
    Эндпоинт для получения списка фильмов
    с возможностью фильтрации по жанру и сортировке по рейтингу.
    """
    return await film_service.list_films(request_params)


@router.get(
    "/search",
    response_model=list[FilmShort],
    summary="Найти фильмы по имени",
    tags=["Полнотекстовый поиск"],
)
async def films_search(
    request_params: Annotated[
        ServiceFilmSearchParamsModel, Depends(get_film_search_service_params)
    ],
    film_service: Annotated[FilmService, Depends(get_film_service)],
) -> list[dict[str, str]]:
    return await film_service.search_films(request_params)


@router.get(
    "/{film_id}", response_model=FilmDetail, summary="Получить детальное описание фильма по id"
)
async def film_details(
    film_id: UUID4,
    access_labels: Annotated[list[AccessLabel], Depends(user_access_labels)],
    film_service: Annotated[FilmService, Depends(get_film_service)],
) -> dict[str, Any]:
    try:
        return await film_service.get_film_by_id(film_id, access_labels)
    except FilmNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="film not found")
    except FilmAccessError:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN, detail="film access error")

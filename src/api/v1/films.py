import logging
from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4

from models.film import Film, FilmDetail
from services.film import FilmService

from .dependencies import get_film_service
from .schemas import FilmListParams, FilmSearchParams

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/",
            response_model=List[Film],
            summary="Получить список популярных фильмов")
async def films(
    query_params: FilmListParams = Depends(),
    film_service: FilmService = Depends(get_film_service),
    ) -> List[Film]:
    """
    Эндпоинт для получения списка фильмов 
    с возможностью фильтрации по жанру и сортировке по рейтингу.
    """
    film_list = await film_service.get_films(query_params)
    return film_list.items


@router.get("/search",
            response_model=List[Film],
            summary="Найти фильмы по имени",
            tags=['Полнотекстовый поиск'])
async def films_search(
    query_params: FilmSearchParams = Depends(),
    film_service: FilmService = Depends(get_film_service)
    ) -> List[Film]:
    """
    Эндпоинт для поиска фильмов по ключевым словам.
    """
    film_list = await film_service.get_films(query_params)
    return film_list.items


@router.get("/{film_id}",
            response_model=FilmDetail,
            summary="Получить детальное описание фильма по id")
async def film_details(
    film_id: UUID4,
    film_service: FilmService = Depends(get_film_service)
    ) -> FilmDetail:
    """
    Детали фильма
    """
    film = await film_service.get_film_by_id(film_id)
    if not film:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='film not found'
            )

    return film

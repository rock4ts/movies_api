from http import HTTPStatus
from typing import List
import fastapi
from pydantic import UUID4
import logging
from models.genre import Genre
from services.genre import GenreService, get_genre_service


logger = logging.getLogger(__name__)

router = fastapi.APIRouter()


# для эндпоинта /genres
@router.get(
    "", response_model=List[Genre], summary="Список жанров",
)
async def genres(
    genre_service: GenreService = fastapi.Depends(get_genre_service)
) -> List[Genre]:
    """
    Эндпоинт для получения списка всех жанров
    """
    genres = await genre_service.get_all()
    return genres


# для эндпоинта /genres/{uuid}
@router.get(
    "/{uuid}", response_model=Genre, summary="Данные по конкретному жанру"
)
async def genre_details(
    uuid: UUID4,
    genre_service: GenreService = fastapi.Depends(get_genre_service)
) -> Genre:
    """
    Детали по жанру
    """
    genre = await genre_service.get_by_id(str(uuid))
    if not genre:
        raise fastapi.HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail='genre not found'
        )

    return genre

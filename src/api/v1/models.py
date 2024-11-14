from typing import Any, Optional
from fastapi import Depends
from pydantic import UUID4, BaseModel, Field


class PaginationParams(BaseModel):
    page_size: Optional[int] = Field(50, description="Количество объектов на странице.", ge=1, le=100)
    page_number: Optional[int] = Field(1, description="Номер страницы.", ge=1)


class FilmListParams(BaseModel):
    sort: Optional[str] = Field(
        None,
        examples=['-imdb_rating'],
        description="Поле сортировки, напр. по убыванию рейтинга: `?sort=-imdb_rating`."
        )
    genre_id: Optional[UUID4] = Field(
        None,
        description="UUID жанра для фильтрации фильмов.",
        validation_alias="genre"
        )
    pagination_params: PaginationParams = Depends()


class FilmSearchParams(FilmListParams):
    query: Optional[str] = None


class FilmElasticParams(BaseModel):
    sorts: list[dict[str, Any]]
    filters: list[dict[str, Any]]
    musts: list[dict[str, Any]]
    from_: int = 0
    size: int = 50

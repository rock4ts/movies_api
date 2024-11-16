from typing import Optional

from fastapi import Depends
from pydantic import UUID4, BaseModel, Field, model_serializer


class PaginationParams(BaseModel):
    page_size: Optional[int] = Field(
        50, description="Количество объектов на странице.", ge=1, le=100
        )
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

    @model_serializer(mode='wrap')
    def serialize(self, handler) -> dict:
        data = handler(self)
        pagination_data = data.pop("pagination_params", {})
        return {**data, **pagination_data}


class FilmSearchParams(FilmListParams):
    query: Optional[str] = Field(
        None,
        examples=['star'],
        description="Поле для полнотекстового поиска по названию фильма."
    )

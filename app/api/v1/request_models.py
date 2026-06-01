from typing import Literal, Self

from pydantic import UUID4, BaseModel, Field, model_validator


class PaginationParams(BaseModel):
    page_size: int | None = Field(50, description="Количество объектов на странице.", ge=1, le=100)
    page_number: int | None = Field(1, description="Номер страницы.", ge=1, le=100)

    @model_validator(mode="after")
    def validate_pagination_params(self) -> Self:
        if self.page_size and not self.page_number:
            raise ValueError("Page number is required")
        if self.page_number and not self.page_size:
            raise ValueError("Page size is required")
        return self


class FilmListParams(PaginationParams):
    sort: Literal["-imdb_rating", "imdb_rating"] | None = Field(
        None,
        examples=["-imdb_rating", "imdb_rating"],
        description="Поле сортировки, напр. по убыванию рейтинга: `?sort=-imdb_rating`.",
    )
    genre_id: UUID4 | None = Field(
        None, description="UUID жанра для фильтрации фильмов.", alias="genre"
    )


class FilmSearchParams(PaginationParams):
    query: str | None = Field(
        None, examples=["star"], description="Поле для полнотекстового поиска по названию фильма."
    )


class PersonSearchParams(PaginationParams):
    query: str | None = Field(
        None, examples=["Leonard"], description="Поле для полнотекстового поиска по имени персоны."
    )

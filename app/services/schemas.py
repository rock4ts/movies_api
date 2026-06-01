from typing import Literal, Self

from pydantic import UUID4, BaseModel, Field, model_validator


class PaginationParamsDTO(BaseModel):
    page_size: int | None = Field(50, ge=1, le=100)
    page_number: int | None = Field(1, ge=1, le=100)

    @model_validator(mode="after")
    def validate_pagination_params(self) -> Self:
        if self.page_size and not self.page_number:
            raise ValueError("Page number is required")
        if self.page_number and not self.page_size:
            raise ValueError("Page size is required")
        return self


class FilmListParamsDTO(PaginationParamsDTO):
    sort: Literal["-imdb_rating", "imdb_rating"] | None = None
    genre_id: UUID4 | None = Field(None, alias="genre")


class FilmSearchParamsDTO(PaginationParamsDTO):
    query: str | None = None


class PersonSearchParamsDTO(PaginationParamsDTO):
    query: str | None = None

from typing import List
from pydantic import BaseModel, UUID4, Field


class Genre(BaseModel):
    uuid: UUID4 = Field(alias='id')
    name: str

    class Config:
        # Разрешает использование оригинального имени при сериализации
        allow_population_by_field_name = True


# Обёртка для списка жанров
class GenreList(BaseModel):
    genres: List[Genre]

from typing import List
from pydantic import AliasChoices, BaseModel, UUID4, Field


validation_choises = AliasChoices('uuid', 'id')


class Genre(BaseModel):
    uuid: UUID4 = Field(validation_alias=AliasChoices('id', 'uuid'))
    name: str


# Обёртка для списка жанров
class GenreList(BaseModel):
    genres: List[Genre]

from pydantic import UUID4, AliasChoices, Field, BaseModel

from .genre import Genre
from .person import PersonShort


class FilmShort(BaseModel):
    uuid: UUID4 = Field(validation_alias=AliasChoices("id", "uuid"))
    title: str
    imdb_rating: float | None = None


class FilmDetail(BaseModel):
    uuid: UUID4 = Field(validation_alias=AliasChoices("id", "uuid"))
    title: str
    imdb_rating: float | None = None
    # description: str|None = None
    genre: list[Genre] = Field(validation_alias=AliasChoices("genres", "genre"))
    actors: list[PersonShort]
    writers: list[PersonShort]
    directors: list[PersonShort]

from pydantic import UUID4, AliasChoices, Field

from .base import Item, ItemList
from .genre import Genre
from .person import PersonShort


class Film(Item):
    uuid: UUID4 = Field(validation_alias=AliasChoices('id', 'uuid'))
    title: str
    imdb_rating: float|None = None


class FilmList(ItemList):
    items: list[Film] = []


class FilmDetail(Item):
    uuid: UUID4 = Field(validation_alias=AliasChoices('id', 'uuid'))
    title: str
    imdb_rating: float|None = None
    # description: str|None = None
    genre: list[Genre] = Field(validation_alias=AliasChoices('genres', 'genre'))
    actors: list[PersonShort]
    writers: list[PersonShort]
    directors: list[PersonShort]

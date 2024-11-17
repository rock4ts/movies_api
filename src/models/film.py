from typing import List, Optional

from pydantic import UUID4, AliasChoices, Field

from .base import Item, ItemList
from .genre import Genre
from .person import PersonShort


class Film(Item):
    uuid: UUID4 = Field(validation_alias=AliasChoices('id', 'uuid'))
    title: str
    imdb_rating: Optional[float] = None


class FilmList(ItemList):
    items: list[Film] = []


class FilmDetail(Item):
    uuid: UUID4 = Field(validation_alias=AliasChoices('id', 'uuid'))
    title: str
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    genre: List[Genre] = Field(validation_alias=AliasChoices('genres', 'genre'))
    actors: List[PersonShort]
    writers: List[PersonShort]
    directors: List[PersonShort]

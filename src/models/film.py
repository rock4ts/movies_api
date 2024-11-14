from typing import List, Optional
from pydantic import BaseModel, UUID4, Field
from models.genre import Genre
from models.person import PersonShort


class Film(BaseModel):
    uuid: UUID4 = Field(validation_alias='id')
    title: str
    imdb_rating: Optional[float] = None


class FilmDetail(BaseModel):
    uuid: UUID4 = Field(validation_alias='id')
    title: str
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    genre: List[Genre] = Field(validation_alias='genres')
    actors: List[PersonShort]
    writers: List[PersonShort]
    directors: List[PersonShort]

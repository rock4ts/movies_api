from typing import List, Optional
from pydantic import BaseModel, UUID4
from models.genre import Genre
from models.person import Person


class Film(BaseModel):
    uuid: UUID4
    title: str
    imdb_rating: Optional[float] = None


class FilmDetail(BaseModel):
    uuid: UUID4
    title: str
    imdb_rating: Optional[float] = None
    description: Optional[str] = None
    genre: List[Genre] = []
    actors: List[Person] = []
    writers: List[Person] = []
    directors: List[Person] = []

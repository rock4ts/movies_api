from typing import List, Optional
from pydantic import BaseModel, UUID4


class PersonFilmList(BaseModel):
    uuid: UUID4
    roles: Optional[List[str]] = []


class Person(BaseModel):
    uuid: UUID4
    full_name: str
    films: Optional[List[PersonFilmList]] = []

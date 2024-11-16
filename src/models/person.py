from typing import List, Optional
from pydantic import AliasChoices, BaseModel, UUID4, Field


class PersonFilmList(BaseModel):
    uuid: UUID4 = Field(validation_alias='id')
    roles: List[str]


class PersonShort(BaseModel):
    uuid: UUID4 = Field(validation_alias=AliasChoices('id', 'uuid'))
    full_name: str


class Person(BaseModel):
    uuid: UUID4 = Field(validation_alias='id')
    full_name: str
    films: Optional[List[PersonFilmList]] = []

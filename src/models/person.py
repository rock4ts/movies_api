from typing import List, Optional
from pydantic import AliasChoices, BaseModel, UUID4, Field


class PersonFilmList(BaseModel):
    uuid: UUID4 = Field(validation_alias=AliasChoices('id', 'uuid'))
    roles: List[str]


class PersonShort(BaseModel):
    uuid: UUID4 = Field(validation_alias=AliasChoices('id', 'uuid'))
    full_name: str = Field(validation_alias=AliasChoices('name', 'full_name'))


class Person(BaseModel):
    uuid: UUID4 = Field(validation_alias=AliasChoices('id', 'uuid'))
    full_name: str
    films: Optional[List[PersonFilmList]] = []


class PersonList(BaseModel):
    items: List[Person] = None

from pydantic import UUID4, AliasChoices, BaseModel, Field


class PersonFilmList(BaseModel):
    uuid: UUID4 = Field(validation_alias=AliasChoices("id", "uuid"))
    roles: list[str]


class PersonShort(BaseModel):
    uuid: UUID4 = Field(validation_alias=AliasChoices("id", "uuid"))
    full_name: str = Field(validation_alias=AliasChoices("name", "full_name"))


class Person(BaseModel):
    uuid: UUID4 = Field(validation_alias=AliasChoices("id", "uuid"))
    full_name: str
    films: list[PersonFilmList] | None = []

from pydantic import AliasChoices, BaseModel, UUID4, Field


class Genre(BaseModel):
    uuid: UUID4 = Field(validation_alias=AliasChoices('id', 'uuid'))
    name: str

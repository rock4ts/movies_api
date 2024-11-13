from pydantic import BaseModel, UUID4, Field


class Genre(BaseModel):
    uuid: UUID4 = Field(validation_alias='id')
    name: str

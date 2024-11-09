from pydantic import BaseModel, UUID4


class Genre(BaseModel):
    uuid: UUID4
    name: str

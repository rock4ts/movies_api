from typing import List, Optional
from pydantic import BaseModel, UUID4


class Person(BaseModel):
    uuid: UUID4
    full_name: str
    roles: Optional[List[str]] = []

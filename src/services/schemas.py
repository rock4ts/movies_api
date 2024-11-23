from typing import Any

from pydantic import BaseModel

ListDictAny = list[dict[str, Any]]


class ElasticSearchParams(BaseModel):
    sorts: ListDictAny|None = []
    filters: ListDictAny|None = []
    musts: ListDictAny|None = []
    from_: int|None = 0
    size: int|None = 50


class PersonElasticParams(BaseModel):
    musts: list[dict[str, Any]]
    from_: int = 0
    size: int = 50

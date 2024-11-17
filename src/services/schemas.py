from typing import Any, Optional

from pydantic import BaseModel

ListDictAny = list[dict[str, Any]]


class ElasticSearchParams(BaseModel):
    sorts: Optional[ListDictAny] = []
    filters: Optional[ListDictAny] = []
    musts: Optional[ListDictAny] = []
    from_: Optional[int] = 0
    size: Optional[int] = 50


class PersonElasticParams(BaseModel):
    musts: list[dict[str, Any]]
    from_: int = 0
    size: int = 50

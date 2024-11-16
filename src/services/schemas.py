from typing import Any

from pydantic import BaseModel


class ElasticSearchParams(BaseModel):
    sorts: list[dict[str, Any]]
    filters: list[dict[str, Any]]
    musts: list[dict[str, Any]]
    from_: int = 0
    size: int = 50
import abc
from typing import Union

from pydantic import BaseModel


class BaseService(abc.ABC):
    def _create_redis_key(self,
                          index: str,
                          params: Union[list, BaseModel]) -> str:
        if isinstance(params, BaseModel):
            vals = list(map(str, params.model_dump(mode='json').values()))
        else:
            vals = list(map(str, params))

        vals.sort()
        key = f"{index}:" + ':'.join(vals)

        return key

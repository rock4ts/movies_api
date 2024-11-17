from pydantic import BaseModel


class Item(BaseModel):
    pass


class ItemList(BaseModel):
    items: list[Item] = []

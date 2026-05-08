from pydantic import BaseModel


class ItemResponse(BaseModel):
    item_id: int
    item_name: str
    cuisine: str


class ItemListResponse(BaseModel):
    items: list[ItemResponse]

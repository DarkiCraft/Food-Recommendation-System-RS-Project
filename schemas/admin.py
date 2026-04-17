from pydantic import BaseModel

class ItemCreateRequest(BaseModel):
    item_name: str
    cuisine: str

class SystemStatsResponse(BaseModel):
    total_users: int
    total_items: int
    total_interactions: int
    total_orders: int

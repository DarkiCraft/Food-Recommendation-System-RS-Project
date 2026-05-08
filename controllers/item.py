from fastapi import APIRouter, Depends, Query

from dependencies import get_item_service
from schemas.item import ItemListResponse, ItemResponse
from services.item import ItemService


router = APIRouter(prefix="/items", tags=["items"])


@router.get("/", response_model=ItemListResponse)
def get_items(
        item_ids: list[int] = Query(default=[]),
        service: ItemService = Depends(get_item_service)
):
    return service.get_items(item_ids=item_ids or None)


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(
        item_id: int,
        service: ItemService = Depends(get_item_service)
):
    return service.get_item(item_id)

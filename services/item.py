from fastapi import HTTPException, status

from repos.item import ItemRepo
from schemas.item import ItemResponse, ItemListResponse


class ItemService:
    def __init__(self, item_repo: ItemRepo):
        self.__item_repo = item_repo

    def get_items(self, item_ids: list[int] | None = None) -> ItemListResponse:
        if item_ids:
            items = self.__item_repo.get_by_ids(item_ids)
            item_by_id = {item.item_id: item for item in items}
            ordered_items = [item_by_id[item_id] for item_id in item_ids if item_id in item_by_id]
        else:
            ordered_items = self.__item_repo.get_all()

        return ItemListResponse(
            items=[
                ItemResponse(
                    item_id=item.item_id,
                    item_name=item.item_name,
                    cuisine=item.cuisine
                )
                for item in ordered_items
            ]
        )

    def get_item(self, item_id: int) -> ItemResponse:
        item = self.__item_repo.get_by_id(item_id)
        if item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

        return ItemResponse(
            item_id=item.item_id,
            item_name=item.item_name,
            cuisine=item.cuisine
        )

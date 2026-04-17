from fastapi import HTTPException, status

from models.item import ItemModel
from repos.interaction import InteractionRepo
from repos.item import ItemRepo
from repos.order import OrderRepo
from repos.user import UserRepo
from schemas.admin import ItemCreateRequest, SystemStatsResponse

class AdminService:
    def __init__(
            self,
            user_repo: UserRepo,
            item_repo: ItemRepo,
            interaction_repo: InteractionRepo,
            order_repo: OrderRepo
    ):
        self.__user_repo = user_repo
        self.__item_repo = item_repo
        self.__interaction_repo = interaction_repo
        self.__order_repo = order_repo

    def create_item(self, request: ItemCreateRequest) -> ItemModel:
        item = ItemModel(
            item_name=request.item_name,
            cuisine=request.cuisine
        )
        return self.__item_repo.create(item)

    def delete_item(self, item_id: int):
        item = self.__item_repo.delete(item_id)
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    def get_system_stats(self) -> SystemStatsResponse:
        users = len(self.__user_repo.get_all())
        items = len(self.__item_repo.get_all())
        interactions = len(self.__interaction_repo.get_all())
        orders = len(self.__order_repo.get_all())
        return SystemStatsResponse(
            total_users=users,
            total_items=items,
            total_interactions=interactions,
            total_orders=orders
        )

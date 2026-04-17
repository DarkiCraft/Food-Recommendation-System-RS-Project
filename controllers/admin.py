from fastapi import APIRouter, Depends

from dependencies import get_recommendation_service, get_admin_service, get_admin_token
from schemas.admin import ItemCreateRequest, SystemStatsResponse
from services.admin import AdminService
from services.recommend import RecommendationService

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(get_admin_token)])


@router.post("/items")
def create_item(
        request: ItemCreateRequest,
        service: AdminService = Depends(get_admin_service)
):
    item = service.create_item(request)
    return {"message": "Item created", "item_id": item.item_id}

@router.delete("/items/{item_id}")
def delete_item(
        item_id: int,
        service: AdminService = Depends(get_admin_service)
):
    service.delete_item(item_id)
    return {"message": f"Item {item_id} deleted"}

@router.get("/stats", response_model=SystemStatsResponse)
def get_stats(
        service: AdminService = Depends(get_admin_service)
):
    return service.get_system_stats()

@router.post("/retrain")
def retrain(
        service: RecommendationService = Depends(get_recommendation_service)
):
    service.retrain()
    return {"message": "Retrain complete"}

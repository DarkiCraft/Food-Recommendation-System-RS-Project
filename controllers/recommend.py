from fastapi import APIRouter, Depends, Query

from dependencies import get_current_user, get_recommendation_service
from schemas.recommend import RecommendRequest
from services.recommend import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/")
def get_recommendations(
        k: list[int] = Query(default=[5]),
        user_id: int = Depends(get_current_user),
        service: RecommendationService = Depends(get_recommendation_service)
):
    request = RecommendRequest(k=k)
    result = service.recommend(request, user_id)
    if isinstance(result, dict):
        return {"recommendations_by_k": result}
    return {"recommendations": result}
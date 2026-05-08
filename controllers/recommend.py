from fastapi import APIRouter, Depends, Query

from dependencies import get_current_user, get_recommendation_service
from schemas.recommend import RecommendResponse
from services.recommend import RecommendationService

router = APIRouter(prefix="/recommendations", tags=["recommendations"])


@router.get("/", response_model=RecommendResponse)
def get_recommendations(
        k: int = Query(default=10, ge=1),
        user_id: int = Depends(get_current_user),
        service: RecommendationService = Depends(get_recommendation_service)
):
    return service.recommend(k=k, user_id=user_id)
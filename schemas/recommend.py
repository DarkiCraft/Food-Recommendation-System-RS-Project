from pydantic import BaseModel

class RecommendRequest(BaseModel):
    k: list[int]

class RecommendResponse(BaseModel):
    recommendations: list[int]
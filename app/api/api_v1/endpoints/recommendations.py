from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.ai_schemas import RecommendationsRequest, RecommendationsResponse
from app.services.ai_service import ai_service
from app.core.config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/get", response_model=RecommendationsResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/hour")
async def get_recommendations(request: Request, rec_request: RecommendationsRequest):
    """
    Generate personalized learning recommendations based on user progress.
    Analyzes weak areas and suggests targeted improvements.
    """
    try:
        result = await ai_service.generate_recommendations(
            user_progress=rec_request.userProgress.dict()
        )
        
        return RecommendationsResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate recommendations: {str(e)}"
        )


@router.get("/health")
async def recommendations_health():
    """Check if the recommendations service is working"""
    try:
        # Test with sample progress
        test_progress = {
            "totalWords": 50,
            "masteredWords": 15,
            "weakAreas": ["verbs", "past_tense"],
            "averageAccuracy": 75.0
        }
        
        test_result = await ai_service.generate_recommendations(test_progress)
        return {
            "status": "healthy",
            "ai_model": settings.OLLAMA_MODEL,
            "test_recommendations": len(test_result.get("recommendations", []))
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

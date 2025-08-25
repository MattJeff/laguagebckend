from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.ai_schemas import TestGenerateRequest, TestGenerateResponse
from app.services.ai_service import ai_service
from app.core.config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/create", response_model=TestGenerateResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/hour")
async def create_test(request: Request, test_request: TestGenerateRequest):
    """
    Generate AI-powered adaptive tests with CEFR level targeting.
    Creates progressive difficulty questions for vocabulary assessment.
    """
    try:
        result = await ai_service.generate_test_questions(
            user_words=test_request.userWords,
            test_type=test_request.testType,
            target_level=test_request.targetLevel,
            question_count=test_request.questionCount
        )
        
        return TestGenerateResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create test: {str(e)}"
        )


@router.get("/health")
async def tests_health():
    """Check if the test generation service is working"""
    try:
        # Test with sample words
        test_words = [
            {"word": "hello", "translation": "bonjour", "definition": "a greeting"},
            {"word": "world", "translation": "monde", "definition": "the earth"}
        ]
        
        test_result = await ai_service.generate_test_questions(test_words, "vocabulary", 2)
        return {
            "status": "healthy",
            "ai_model": settings.OLLAMA_MODEL,
            "test_questions": len(test_result.get("questions", []))
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

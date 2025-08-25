from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.ai_schemas import WordAnalyzeRequest, WordAnalyzeResponse
from app.services.ai_service import ai_service
from app.core.config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/analyze", response_model=WordAnalyzeResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/hour")
async def analyze_word(request: Request, word_request: WordAnalyzeRequest):
    """
    Analyze a word using AI to get contextual French translation and linguistic data.
    Core enrichment service for Netflix English Learner extension.
    """
    try:
        result = await ai_service.analyze_word(
            word=word_request.word,
            context=word_request.context,
            langue_output=word_request.langue_output,
            user_level=word_request.userLevel
        )
        
        return WordAnalyzeResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze word: {str(e)}"
        )


@router.get("/health")
async def words_health():
    """Check if the word analysis service is working"""
    try:
        # Test with a simple word
        test_result = await ai_service.analyze_word("hello", "Hello, how are you?")
        return {
            "status": "healthy",
            "ai_model": settings.OLLAMA_MODEL,
            "test_word": test_result.get("word", "failed")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

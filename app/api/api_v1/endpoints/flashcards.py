from fastapi import APIRouter, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.ai_schemas import FlashcardGenerateRequest, FlashcardGenerateResponse
from app.services.ai_service import ai_service
from app.core.config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.post("/generate", response_model=FlashcardGenerateResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/hour")
async def generate_flashcards(request: Request, flashcard_request: FlashcardGenerateRequest):
    """
    Generate 4 types of intelligent flashcards with adaptive selection.
    Types: classic (free), contextual (recommended), audio (premium), speed (premium).
    """
    try:
        # Convert words to dict format for AI service
        words_data = [word.dict() for word in flashcard_request.words]
        session_config = flashcard_request.sessionConfig.dict()
        
        result = await ai_service.generate_flashcards(
            words_data=words_data,
            session_config=session_config
        )
        
        return FlashcardGenerateResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate flashcards: {str(e)}"
        )


@router.get("/health")
async def flashcards_health():
    """Check if the flashcard generation service is working"""
    try:
        # Test with sample words
        test_words = [
            {"word": "hello", "translation": "bonjour"},
            {"word": "world", "translation": "monde"}
        ]
        
        test_result = await ai_service.generate_flashcards(test_words, "review")
        return {
            "status": "healthy",
            "ai_model": settings.OLLAMA_MODEL,
            "test_flashcards": len(test_result.get("flashcards", []))
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

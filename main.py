#!/usr/bin/env python3
"""
Multilingual AI Flashcard Backend - Production Ready
FastAPI server with MLX-LM for local AI inference
Clean, modular, extensible architecture
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.schemas.ai_schemas import (
    WordAnalysisRequest, WordAnalysisResponse,
    WordTranslationRequest, WordTranslationResponse,
    FlashcardGenerateRequest, FlashcardGenerateResponse,
    TestGenerateRequest, TestGenerateResponse,
    RecommendationsRequest, RecommendationsResponse
)
from app.services.ai_factory import AIServiceFactory
from app.core.config import settings
import uvicorn
import time
import logging

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize AI service using factory
ai_service = AIServiceFactory.create_ai_service()

app = FastAPI(
    title="Multilingual AI Flashcard Backend",
    description="AI-powered multilingual flashcard generation and word analysis",
    version="2.0.0"
)

# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware for Chrome extension
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins including Chrome extensions
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Include OPTIONS for preflight
    allow_headers=["*"],
)

@app.get("/")
async def root():
    service_info = AIServiceFactory.get_service_info()
    return {
        "message": "Multilingual AI Flashcard Backend", 
        "version": "2.1.0",
        "ai_engine": service_info["selected_service"],
        "environment": service_info["environment"],
        "model": service_info["model"],
        "endpoints": [
            "/api/v1/words/analyze",
            "/api/v1/words/translate-and-analyze", 
            "/api/v1/flashcards/generate",
            "/api/v1/tests/create",
            "/api/v1/recommendations/get"
        ]
    }

@app.get("/health")
async def health_check():
    service_info = AIServiceFactory.get_service_info()
    return {
        "status": "healthy", 
        "service": "multilingual_ai_backend", 
        "ai_engine": ai_service.get_engine_name(), 
        "timestamp": int(time.time()), 
        "version": "2.1.1"
    }

# === WORD ANALYSIS ENDPOINTS ===

@app.post("/api/v1/words/analyze", response_model=WordAnalysisResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/hour")
async def analyze_word(request: Request, word_request: WordAnalysisRequest):
    """Analyze a word with known translation"""
    try:
        logger.info(f"Analyzing word: {word_request.word}")
        result = await ai_service.analyze_word(
            word=word_request.word,
            context=word_request.context,
            langue_output=word_request.langue_output,
            user_level=word_request.userLevel
        )
        return WordAnalysisResponse(**result)
    except Exception as e:
        logger.error(f"Word analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Word analysis failed: {str(e)}")

@app.post("/api/v1/words/translate-and-analyze", response_model=WordTranslationResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/hour")
async def translate_and_analyze_word(request: Request, word_request: WordTranslationRequest):
    """AI auto-translates unknown word and provides complete analysis"""
    try:
        logger.info(f"Translating and analyzing word: {word_request.word.text}")
        result = await ai_service.translate_and_analyze_word(
            word=word_request.word.text,
            context=word_request.word.context,
            source_lang=word_request.config.sourceLanguage,
            target_lang=word_request.config.targetLanguage,
            user_level=word_request.config.userLevel,
            mastery_level=word_request.word.masteryLevel
        )
        return WordTranslationResponse(**result)
    except Exception as e:
        logger.error(f"Translation and analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Translation and analysis failed: {str(e)}")

# === FLASHCARD GENERATION ===

@app.post("/api/v1/flashcards/generate", response_model=FlashcardGenerateResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/hour")
async def generate_flashcards(request: Request, flashcard_request: FlashcardGenerateRequest):
    """Generate multilingual flashcards using AI service"""
    try:
        logger.info(f"Generating flashcards for {len(flashcard_request.words)} words")
        words_data = [word.model_dump() for word in flashcard_request.words]
        session_config = flashcard_request.sessionConfig.model_dump()
        
        result = await ai_service.generate_flashcards(words_data, session_config)
        return FlashcardGenerateResponse(**result)
    except Exception as e:
        logger.error(f"Flashcard generation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Flashcard generation failed: {str(e)}")

# === TEST CREATION ===

@app.post("/api/v1/tests/create", response_model=TestGenerateResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/hour")
async def create_test(request: Request, test_request: TestGenerateRequest):
    """Create adaptive test using AI service"""
    try:
        logger.info(f"Creating test with {test_request.questionCount} questions")
        result = await ai_service.create_test(
            user_words=test_request.userWords,
            test_type=test_request.testType,
            target_level=test_request.targetLevel,
            question_count=test_request.questionCount
        )
        return TestGenerateResponse(**result)
    except Exception as e:
        logger.error(f"Test creation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test creation failed: {str(e)}")

# === RECOMMENDATIONS ===

@app.post("/api/v1/recommendations/get", response_model=RecommendationsResponse)
@limiter.limit(f"{settings.RATE_LIMIT_REQUESTS}/hour")
async def get_recommendations(request: Request, rec_request: RecommendationsRequest):
    """Get personalized learning recommendations using AI service"""
    try:
        logger.info("Generating personalized recommendations")
        user_progress_dict = rec_request.userProgress.model_dump() if rec_request.userProgress else {}
        
        result = await ai_service.generate_recommendations(
            user_progress=user_progress_dict
        )
        return RecommendationsResponse(**result)
    except Exception as e:
        logger.error(f"Recommendations failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")

# === HEALTH ENDPOINTS ===

@app.get("/api/v1/test")
async def test_ollama():
    """Simple test endpoint for Ollama functionality"""
    try:
        result = await ai_service._generate_completion("Say hello in French", "You are a helpful assistant.")
        return {"status": "success", "response": result}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/api/v1/simple-analyze")
async def simple_analyze(request: dict):
    """Simplified word analysis without complex JSON parsing"""
    try:
        word = request.get("word", "")
        prompt = f"Translate '{word}' to English and give a brief definition."
        result = await ai_service._generate_completion(prompt, "You are a translator.")
        return {"word": word, "analysis": result}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/v1/words/health")
async def words_health():
    service_info = AIServiceFactory.get_service_info()
    return {"status": "healthy", "service": "word_analysis", "ai_engine": service_info["selected_service"]}

@app.get("/api/v1/flashcards/health")
async def flashcards_health():
    service_info = AIServiceFactory.get_service_info()
    return {"status": "healthy", "service": "flashcard_generation", "ai_engine": service_info["selected_service"]}

@app.get("/api/v1/tests/health")
async def tests_health():
    service_info = AIServiceFactory.get_service_info()
    return {"status": "healthy", "service": "test_creation", "ai_engine": service_info["selected_service"]}

@app.get("/api/v1/recommendations/health")
async def recommendations_health():
    service_info = AIServiceFactory.get_service_info()
    return {"status": "healthy", "service": "recommendations", "ai_engine": service_info["selected_service"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

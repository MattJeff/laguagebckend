from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.services.mlx_ai_service import mlx_ai_service
from app.schemas.ai_schemas import (
    WordAnalyzeRequest, WordAnalyzeResponse,
    FlashcardGenerateRequest, FlashcardGenerateResponse,
    TestGenerateRequest, TestGenerateResponse,
    RecommendationsRequest, RecommendationsResponse
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Load MLX model
    print("🚀 Starting Netflix English Learner AI API with MLX-LM...")
    yield
    # Shutdown
    print("🛑 Shutting down API...")

app = FastAPI(
    title="Netflix English Learner AI API",
    description="AI-powered backend for French learners using MLX-LM",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Netflix English Learner AI API",
        "version": "1.0.0",
        "ai_engine": "MLX-LM + Llama 3.1 8B",
        "services": ["word-analysis", "flashcard-generation", "adaptive-tests", "recommendations"]
    }

@app.get("/health")
async def health_check():
    model_status = "ready" if mlx_ai_service.model else "not_loaded"
    return {
        "status": "healthy",
        "ai_service": model_status,
        "model": mlx_ai_service.model_name
    }

@app.post("/api/v1/words/analyze", response_model=WordAnalyzeResponse)
async def analyze_word(request: WordAnalyzeRequest):
    """Analyze English word for French learners using MLX-LM"""
    try:
        result = await mlx_ai_service.analyze_word(
            word=request.word,
            context=request.context,
            langue_output=request.langue_output,
            user_level=request.userLevel
        )
        return WordAnalyzeResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Word analysis failed: {str(e)}")

@app.post("/api/v1/flashcards/generate", response_model=FlashcardGenerateResponse)
async def generate_flashcards(request: FlashcardGenerateRequest):
    """Generate intelligent flashcards using MLX-LM"""
    try:
        session_config_dict = request.sessionConfig.model_dump() if request.sessionConfig else {}
        words_data = [word.model_dump() for word in request.words]
        
        result = await mlx_ai_service.generate_flashcards(
            words_data=words_data,
            session_config=session_config_dict
        )
        return FlashcardGenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flashcard generation failed: {str(e)}")

@app.post("/api/v1/tests/create", response_model=TestGenerateResponse)
async def create_test(request: TestGenerateRequest):
    """Create adaptive test using MLX-LM"""
    try:
        result = await mlx_ai_service.generate_test_questions(
            user_words=request.userWords,
            test_type=request.testType,
            target_level=request.targetLevel,
            question_count=request.questionCount
        )
        return TestGenerateResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test creation failed: {str(e)}")

@app.post("/api/v1/recommendations/get", response_model=RecommendationsResponse)
async def get_recommendations(request: RecommendationsRequest):
    """Get personalized learning recommendations using MLX-LM"""
    try:
        user_progress_dict = request.userProgress.model_dump() if request.userProgress else {}
        
        result = await mlx_ai_service.generate_recommendations(
            user_progress=user_progress_dict
        )
        return RecommendationsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendations failed: {str(e)}")

# Health endpoints for individual services
@app.get("/api/v1/words/health")
async def words_health():
    return {"status": "healthy", "service": "word_analysis", "ai_engine": "MLX-LM"}

@app.get("/api/v1/flashcards/health")
async def flashcards_health():
    return {"status": "healthy", "service": "flashcard_generation", "ai_engine": "MLX-LM"}

@app.get("/api/v1/tests/health")
async def tests_health():
    return {"status": "healthy", "service": "test_creation", "ai_engine": "MLX-LM"}

@app.get("/api/v1/recommendations/health")
async def recommendations_health():
    return {"status": "healthy", "service": "recommendations", "ai_engine": "MLX-LM"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

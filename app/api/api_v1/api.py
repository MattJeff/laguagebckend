from fastapi import APIRouter
from app.api.api_v1.endpoints import words, flashcards, tests, recommendations

api_router = APIRouter()
api_router.include_router(words.router, prefix="/words", tags=["words"])
api_router.include_router(flashcards.router, prefix="/flashcards", tags=["flashcards"])
api_router.include_router(tests.router, prefix="/tests", tags=["tests"])
api_router.include_router(recommendations.router, prefix="/recommendations", tags=["recommendations"])

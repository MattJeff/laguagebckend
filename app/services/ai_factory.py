"""
AI Service Factory - Automatically selects MLX or Ollama based on environment
"""

import logging
from typing import Union
import platform

# Conditional imports to avoid Railway deployment issues
try:
    # Only import MLX on Apple Silicon (Darwin)
    if platform.system() == "Darwin":
        from app.services.mlx_ai_service import MLXAIService
    else:
        MLXAIService = None
except ImportError:
    MLXAIService = None

from app.services.ollama_ai_service import OllamaAIService
from app.services.openai_ai_service import OpenAIService
from app.services.groq_ai_service import GroqService
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIServiceFactory:
    """Factory to create appropriate AI service based on environment"""
    
    @staticmethod
    def create_ai_service() -> Union["MLXAIService", "OllamaAIService", "OpenAIService", "GroqService"]:
        """Factory method to create appropriate AI service based on configuration"""
        logger.info(f"Creating AI service with mode: {settings.AI_SERVICE}")
        
        if settings.AI_SERVICE == "groq":
            logger.info("Using Groq AI Service")
            return GroqService()
        elif settings.AI_SERVICE == "openai":
            logger.info("Using OpenAI AI Service")
            return OpenAIService()
        elif settings.AI_SERVICE == "mlx":
            if MLXAIService is None:
                logger.warning("MLX not available on this platform. Falling back to Groq.")
                return GroqService()
            logger.info("Using MLX AI Service")
            return MLXAIService()
        elif settings.AI_SERVICE == "ollama":
            logger.info("Attempting Ollama AI Service")
            try:
                service = OllamaAIService()
                logger.info("Ollama AI Service initialized successfully")
                return service
            except Exception as e:
                logger.warning(f"Ollama failed: {e}. Switching to Groq.")
                logger.info("Using Groq AI Service as fallback")
                return GroqService()
        else:
            logger.info("Unknown AI service, defaulting to Groq")
            return GroqService()
    
    @staticmethod
    def get_service_info() -> dict:
        """Get information about the current AI service configuration"""
        service_map = {
            "groq": "Groq",
            "openai": "OpenAI", 
            "mlx": "MLX",
            "ollama": "Ollama"
        }
        
        return {
            "environment": settings.ENVIRONMENT,
            "ai_service_mode": settings.AI_SERVICE,
            "selected_service": service_map.get(settings.AI_SERVICE, "Groq"),
            "model": "llama-3.1-8b-instant" if settings.AI_SERVICE == "groq" else "Various"
        }

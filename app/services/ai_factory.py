"""
AI Service Factory - Automatically selects MLX or Ollama based on environment
"""

import logging
from typing import Union
from app.services.mlx_ai_service import MLXAIService
from app.services.ollama_ai_service import OllamaAIService
from app.services.openai_ai_service import OpenAIService
from app.services.groq_ai_service import GroqService
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIServiceFactory:
    """Factory to create appropriate AI service based on environment"""
    
    @staticmethod
    def create_ai_service() -> Union["MLXAIService", "OllamaAIService", "OpenAIService", "GroqService"]:
        """Create AI service based on configuration and environment"""
        
        # Check for explicit service selection
        if settings.AI_SERVICE == "groq":
            logger.info("Using Groq API Service (Free)")
            return GroqService()
        elif settings.AI_SERVICE == "openai":
            logger.info("Using OpenAI API Service")
            return OpenAIService()
        
        if settings.use_mlx:
            logger.info("Using MLX AI Service (Apple Silicon - Development)")
            try:
                # Import MLX only when needed to avoid Linux compatibility issues
                from app.services.mlx_ai_service import MLXAIService
                return MLXAIService()
            except Exception as e:
                logger.warning(f"MLX initialization failed: {e}. Falling back to Groq.")
                return GroqService()
        else:
            logger.info("Using Ollama AI Service (Production/Server)")
            try:
                return OllamaAIService()
            except Exception as e:
                logger.warning(f"Ollama initialization failed: {e}. Falling back to Groq.")
                return GroqService()
    
    @staticmethod
    def get_service_info() -> dict:
        """Get information about the current AI service configuration"""
        return {
            "environment": settings.ENVIRONMENT,
            "ai_service_mode": settings.AI_SERVICE,
            "use_mlx": settings.use_mlx,
            "use_ollama": settings.use_ollama,
            "selected_service": "MLX" if settings.use_mlx else "Ollama",
            "model": settings.OLLAMA_MODEL if settings.use_ollama else "MLX Local Model"
        }

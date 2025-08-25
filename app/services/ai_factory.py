"""
AI Service Factory - Automatically selects MLX or Ollama based on environment
"""

import logging
from typing import Union
from app.core.config import settings
from app.services.ollama_ai_service import OllamaAIService

logger = logging.getLogger(__name__)

class AIServiceFactory:
    """Factory to create appropriate AI service based on environment"""
    
    @staticmethod
    def create_ai_service() -> Union["MLXAIService", OllamaAIService]:
        """Create AI service based on configuration and environment"""
        
        if settings.use_mlx:
            logger.info("Using MLX AI Service (Apple Silicon - Development)")
            try:
                # Import MLX only when needed to avoid Linux compatibility issues
                from app.services.mlx_ai_service import MLXAIService
                return MLXAIService()
            except Exception as e:
                logger.warning(f"MLX initialization failed: {e}. Falling back to Ollama.")
                return OllamaAIService()
        else:
            logger.info("Using Ollama AI Service (Production/Server)")
            return OllamaAIService()
    
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

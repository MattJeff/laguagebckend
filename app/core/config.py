from pydantic_settings import BaseSettings
from typing import Optional, List
import platform


class Settings(BaseSettings):
    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "phi3:mini"
    
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Multilingual AI Flashcard Backend"
    API_KEY: str = "860e86345239f03e811ba9700e6413efcd8504bd2221be353a9872451eeb4e86"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = "your-openai-api-key-here"
    
    # Groq Configuration (Free API)
    GROQ_API_KEY: str = "your-groq-api-key-here"
    GROQ_MODEL: str = "llama-3.1-8b-instant"
    GROQ_FALLBACK_MODEL: str = "gemma2-9b-it"  # 840 tok/s, $0.05/$0.08 per M tokens
    GROQ_ENABLE_PAID: bool = False  # Set to True to enable paid usage after free limits
    
    # CORS Configuration
    ALLOWED_ORIGINS: str = "http://localhost:3000,https://yourdomain.com"
    
    # Environment
    ENVIRONMENT: str = "development"  # development, production
    LOG_LEVEL: str = "INFO"
    
    # AI Service Configuration
    AI_SERVICE: str = "groq"  # groq, mlx, ollama, openai
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    @property
    def use_mlx(self) -> bool:
        """Determine if MLX should be used based on environment and platform"""
        # Check explicit USE_MLX environment variable first
        import os
        use_mlx_env = os.getenv("USE_MLX", "").lower()
        if use_mlx_env in ["false", "0", "no"]:
            return False
        elif use_mlx_env in ["true", "1", "yes"]:
            return True
            
        if self.AI_SERVICE == "mlx":
            return True
        elif self.AI_SERVICE == "ollama":
            return False
        else:  # auto
            # Use MLX if on Mac (development) and MLX Configuration (can be used on any platform)
            is_mac = platform.system() == "Darwin"
            is_development = self.ENVIRONMENT == "development"
            return False  # Default to False for simplicity
    
    @property
    def use_ollama(self) -> bool:
        """Determine if Ollama should be used"""
        return not self.use_mlx
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables


settings = Settings()

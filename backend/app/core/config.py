"""
Application Configuration using Pydantic Settings.
Manages environment variables and application settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings managed via environment variables."""
    
    # Application
    APP_NAME: str = "SentimentAI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = Field(default=False)
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Supabase PostgreSQL
    SUPABASE_URL: str = Field(default="")
    SUPABASE_KEY: str = Field(default="")
    DATABASE_URL: str = Field(default="")
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "https://ai-mlops.vercel.app",
    ]
    
    # ML Model
    MODEL_PATH: str = "ml/models/sentiment_v2.pkl"
    VECTORIZER_PATH: str = "ml/models/vectorizer_v2.pkl"
    MODEL_VERSION: str = "v2.0"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()

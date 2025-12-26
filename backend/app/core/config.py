"""
Application Configuration using Pydantic Settings.
Manages environment variables and application settings.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache
from typing import Optional
import os
import secrets


class Settings(BaseSettings):
    """Application settings managed via environment variables."""
    
    # Application
    APP_NAME: str = "SentimentAI"
    APP_VERSION: str = "2.1.0"
    DEBUG: bool = Field(default=False)
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    
    # Supabase PostgreSQL
    SUPABASE_URL: str = Field(default="")
    SUPABASE_KEY: str = Field(default="")
    DATABASE_URL: str = Field(default="")
    
    # Security & Authentication
    SECRET_KEY: str = Field(default_factory=lambda: secrets.token_urlsafe(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Redis (optional - for caching)
    REDIS_URL: str = Field(default="")
    CACHE_TTL_SECONDS: int = 3600  # 1 hour
    
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
    
    # MLflow
    MLFLOW_TRACKING_URI: str = Field(default="sqlite:///mlflow.db")
    MLFLOW_EXPERIMENT_NAME: str = "sentiment-analysis"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    RATE_LIMIT_ANONYMOUS: str = "10/minute"
    RATE_LIMIT_AUTHENTICATED: str = "100/minute"
    RATE_LIMIT_BATCH: str = "5/hour"
    
    # Logging
    JSON_LOGS: bool = Field(default=False)  # Enable JSON logging for production
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()


settings = get_settings()


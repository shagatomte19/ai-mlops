"""
Pydantic Schemas for API request/response validation.
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SentimentType(str, Enum):
    """Sentiment classification types."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


# ============ Request Schemas ============

class PredictionRequest(BaseModel):
    """Request schema for single prediction."""
    text: str = Field(..., min_length=1, max_length=5000, description="Text to analyze")
    
    @field_validator('text')
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Text cannot be empty or whitespace only')
        return v.strip()


class BatchPredictionRequest(BaseModel):
    """Request schema for batch predictions."""
    texts: List[str] = Field(..., min_length=1, max_length=100, description="List of texts to analyze")
    
    @field_validator('texts')
    @classmethod
    def texts_must_be_valid(cls, v: List[str]) -> List[str]:
        return [text.strip() for text in v if text.strip()]


class ExportRequest(BaseModel):
    """Request schema for data export."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sentiment_filter: Optional[SentimentType] = None
    format: str = Field(default="json", pattern="^(json|csv)$")
    limit: int = Field(default=1000, le=10000)


# ============ Response Schemas ============

class PredictionResponse(BaseModel):
    """Response schema for single prediction."""
    id: Optional[int] = None
    sentiment: SentimentType
    confidence: float = Field(..., ge=0.0, le=1.0)
    positive_score: float = Field(..., ge=0.0, le=1.0)
    negative_score: float = Field(..., ge=0.0, le=1.0)
    neutral_score: float = Field(default=0.0, ge=0.0, le=1.0)
    model_version: str = "v2.0"
    processing_time_ms: Optional[float] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True


class BatchPredictionResponse(BaseModel):
    """Response schema for batch predictions."""
    results: List[PredictionResponse]
    total_processed: int
    total_time_ms: float


class SentimentDistribution(BaseModel):
    """Sentiment distribution statistics."""
    positive: int
    negative: int
    neutral: int = 0


class RecentPrediction(BaseModel):
    """Simplified prediction for history lists."""
    id: int
    text: str
    sentiment: SentimentType
    confidence: float
    timestamp: datetime


class StatsResponse(BaseModel):
    """Response schema for statistics endpoint."""
    total_predictions: int
    sentiment_distribution: SentimentDistribution
    avg_confidence: Optional[float] = None
    recent_predictions: List[RecentPrediction]
    model_version: str = "v2.0"


class TrendDataPoint(BaseModel):
    """Single data point for trend charts."""
    date: str
    positive: int
    negative: int
    neutral: int = 0
    total: int


class AnalyticsResponse(BaseModel):
    """Response schema for analytics dashboard."""
    total_predictions: int
    sentiment_distribution: SentimentDistribution
    avg_confidence: float
    trend_data: List[TrendDataPoint]
    confidence_distribution: List[dict]  # Histogram buckets
    top_words: dict  # Word frequency


class HealthResponse(BaseModel):
    """Response schema for health check."""
    status: str
    version: str
    model_loaded: bool
    database_connected: bool
    uptime_seconds: float


class ModelInfoResponse(BaseModel):
    """Response schema for model information."""
    version: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    training_samples: Optional[int] = None
    is_active: bool = True

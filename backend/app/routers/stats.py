"""
Stats and Analytics Router - Dashboard data endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from ..core.database import get_db
from ..core.config import settings
from ..services.prediction_service import get_prediction_service
from ..models.schemas import StatsResponse, AnalyticsResponse, SentimentDistribution

router = APIRouter(prefix="/stats", tags=["Statistics"])


@router.get("", response_model=StatsResponse)
async def get_stats(db: Session = Depends(get_db)):
    """
    Get basic statistics and recent predictions.
    
    Returns total counts, sentiment distribution, and recent history.
    """
    service = get_prediction_service(db)
    stats = service.get_stats()
    
    return StatsResponse(
        total_predictions=stats["total_predictions"],
        sentiment_distribution=SentimentDistribution(**stats["sentiment_distribution"]),
        avg_confidence=stats["avg_confidence"],
        recent_predictions=stats["recent_predictions"],
        model_version=settings.MODEL_VERSION
    )


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get detailed analytics for dashboard.
    
    Includes trends, confidence distribution, and word frequency.
    """
    service = get_prediction_service(db)
    
    # Get basic stats
    stats = service.get_stats()
    
    # Get trend data
    trend_data = service.get_trend_data(days=min(days, 30))
    
    # Get confidence distribution
    confidence_dist = service.get_confidence_distribution()
    
    # Get top words
    top_words = service.get_top_words(limit=15)
    
    return AnalyticsResponse(
        total_predictions=stats["total_predictions"],
        sentiment_distribution=SentimentDistribution(**stats["sentiment_distribution"]),
        avg_confidence=stats["avg_confidence"],
        trend_data=trend_data,
        confidence_distribution=confidence_dist,
        top_words=top_words
    )


@router.get("/trends")
async def get_trends(
    days: int = 7,
    db: Session = Depends(get_db)
):
    """
    Get sentiment trend data for charting.
    """
    service = get_prediction_service(db)
    trends = service.get_trend_data(days=min(days, 90))
    return {"trends": [t.model_dump() for t in trends]}


@router.get("/words")
async def get_word_frequency(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Get word frequency analysis for word cloud.
    """
    service = get_prediction_service(db)
    words = service.get_top_words(limit=min(limit, 50))
    return words

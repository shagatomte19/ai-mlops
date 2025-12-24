"""
Prediction Service for database operations.
Handles CRUD operations for predictions and analytics.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from collections import Counter
import re

from ..models.prediction import Prediction, AnalyticsSnapshot
from ..models.schemas import (
    PredictionResponse, SentimentType, TrendDataPoint,
    SentimentDistribution, RecentPrediction
)
from ..core.logging import logger


class PredictionService:
    """Service for prediction-related database operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_prediction(
        self,
        text: str,
        sentiment: str,
        confidence: float,
        positive_score: float,
        negative_score: float,
        neutral_score: float = 0.0,
        model_version: str = "v2.0",
        processing_time_ms: float = 0.0
    ) -> Prediction:
        """Create and store a new prediction."""
        prediction = Prediction(
            text=text,
            sentiment=sentiment,
            confidence=confidence,
            positive_score=positive_score,
            negative_score=negative_score,
            neutral_score=neutral_score,
            model_version=model_version,
            processing_time_ms=processing_time_ms,
        )
        
        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)
        
        logger.debug(f"Created prediction: {prediction.id} - {sentiment}")
        return prediction
    
    def get_prediction(self, prediction_id: int) -> Optional[Prediction]:
        """Get a prediction by ID."""
        return self.db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    def get_recent_predictions(self, limit: int = 10) -> List[Prediction]:
        """Get most recent predictions."""
        return (
            self.db.query(Prediction)
            .order_by(desc(Prediction.created_at))
            .limit(limit)
            .all()
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get overall statistics."""
        total = self.db.query(func.count(Prediction.id)).scalar() or 0
        
        positive = self.db.query(func.count(Prediction.id)).filter(
            Prediction.sentiment == "positive"
        ).scalar() or 0
        
        negative = self.db.query(func.count(Prediction.id)).filter(
            Prediction.sentiment == "negative"
        ).scalar() or 0
        
        neutral = self.db.query(func.count(Prediction.id)).filter(
            Prediction.sentiment == "neutral"
        ).scalar() or 0
        
        avg_confidence = self.db.query(func.avg(Prediction.confidence)).scalar() or 0.0
        
        recent = self.get_recent_predictions(5)
        
        return {
            "total_predictions": total,
            "sentiment_distribution": {
                "positive": positive,
                "negative": negative,
                "neutral": neutral,
            },
            "avg_confidence": round(float(avg_confidence), 4),
            "recent_predictions": [
                {
                    "id": p.id,
                    "text": p.text[:100] + "..." if len(p.text) > 100 else p.text,
                    "sentiment": p.sentiment,
                    "confidence": p.confidence,
                    "timestamp": p.created_at.isoformat() if p.created_at else None,
                }
                for p in recent
            ],
        }
    
    def get_trend_data(self, days: int = 7) -> List[TrendDataPoint]:
        """Get sentiment trends over the last N days."""
        trends = []
        today = datetime.now().date()
        
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            start = datetime.combine(date, datetime.min.time())
            end = datetime.combine(date, datetime.max.time())
            
            positive = self.db.query(func.count(Prediction.id)).filter(
                Prediction.created_at >= start,
                Prediction.created_at <= end,
                Prediction.sentiment == "positive"
            ).scalar() or 0
            
            negative = self.db.query(func.count(Prediction.id)).filter(
                Prediction.created_at >= start,
                Prediction.created_at <= end,
                Prediction.sentiment == "negative"
            ).scalar() or 0
            
            neutral = self.db.query(func.count(Prediction.id)).filter(
                Prediction.created_at >= start,
                Prediction.created_at <= end,
                Prediction.sentiment == "neutral"
            ).scalar() or 0
            
            trends.append(TrendDataPoint(
                date=date.isoformat(),
                positive=positive,
                negative=negative,
                neutral=neutral,
                total=positive + negative + neutral
            ))
        
        return trends
    
    def get_confidence_distribution(self) -> List[Dict[str, Any]]:
        """Get confidence score distribution for histogram."""
        predictions = self.db.query(Prediction.confidence).all()
        
        if not predictions:
            return []
        
        # Create buckets: 0-10%, 10-20%, ..., 90-100%
        buckets = {i: 0 for i in range(10)}
        
        for (conf,) in predictions:
            bucket = min(int(conf * 10), 9)
            buckets[bucket] += 1
        
        return [
            {"range": f"{i*10}-{(i+1)*10}%", "count": count}
            for i, count in buckets.items()
        ]
    
    def get_top_words(self, limit: int = 20) -> Dict[str, Dict[str, int]]:
        """Get top words from positive and negative predictions."""
        def extract_words(texts: List[str]) -> Counter:
            words = []
            stop_words = {'the', 'a', 'an', 'is', 'it', 'this', 'that', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'as', 'by'}
            for text in texts:
                text_words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
                words.extend([w for w in text_words if w not in stop_words])
            return Counter(words)
        
        positive_texts = [p.text for p in self.db.query(Prediction.text).filter(Prediction.sentiment == "positive").limit(500).all()]
        negative_texts = [p.text for p in self.db.query(Prediction.text).filter(Prediction.sentiment == "negative").limit(500).all()]
        
        positive_words = dict(extract_words(positive_texts).most_common(limit))
        negative_words = dict(extract_words(negative_texts).most_common(limit))
        
        return {
            "positive": positive_words,
            "negative": negative_words,
        }
    
    def export_predictions(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sentiment_filter: Optional[str] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Export predictions with optional filters."""
        query = self.db.query(Prediction)
        
        if start_date:
            query = query.filter(Prediction.created_at >= start_date)
        if end_date:
            query = query.filter(Prediction.created_at <= end_date)
        if sentiment_filter:
            query = query.filter(Prediction.sentiment == sentiment_filter)
        
        predictions = query.order_by(desc(Prediction.created_at)).limit(limit).all()
        
        return [p.to_dict() for p in predictions]


def get_prediction_service(db: Session) -> PredictionService:
    """Factory function for prediction service."""
    return PredictionService(db)

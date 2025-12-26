"""
Background Tasks for Predictions.
Async tasks for batch processing and analytics.
"""
from typing import List, Dict, Any
from celery import shared_task
from datetime import datetime, timedelta

from .celery_app import celery_app


@celery_app.task(bind=True, max_retries=3)
def process_batch(self, texts: List[str], user_id: int = None) -> Dict[str, Any]:
    """
    Process a batch of texts for sentiment analysis.
    
    Args:
        texts: List of text strings to analyze
        user_id: Optional user ID for tracking
    
    Returns:
        Dictionary with results and metadata
    """
    from app.services.ml_service import ml_service
    from app.core.database import SessionLocal
    from app.services.prediction_service import PredictionService
    
    try:
        db = SessionLocal()
        service = PredictionService(db)
        results = []
        
        for text in texts:
            try:
                sentiment, confidence, pos, neg, neutral, proc_time = ml_service.predict(text)
                
                prediction = service.create_prediction(
                    text=text,
                    sentiment=sentiment,
                    confidence=confidence,
                    positive_score=pos,
                    negative_score=neg,
                    neutral_score=neutral,
                    model_version=ml_service.model_version,
                    processing_time_ms=proc_time
                )
                
                results.append({
                    "id": prediction.id,
                    "text": text[:50] + "..." if len(text) > 50 else text,
                    "sentiment": sentiment,
                    "confidence": confidence
                })
            except Exception as e:
                results.append({
                    "text": text[:50] + "..." if len(text) > 50 else text,
                    "error": str(e)
                })
        
        db.close()
        
        return {
            "status": "completed",
            "total": len(texts),
            "processed": len([r for r in results if "id" in r]),
            "failed": len([r for r in results if "error" in r]),
            "results": results
        }
        
    except Exception as e:
        self.retry(exc=e, countdown=60)  # Retry after 60 seconds


@celery_app.task
def check_drift() -> Dict[str, Any]:
    """
    Scheduled task to check for data drift.
    Runs daily to monitor model performance.
    """
    from app.services.drift_service import drift_service
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        result = drift_service.detect_drift(db, days=7)
        return result
    finally:
        db.close()


@celery_app.task
def create_analytics_snapshot() -> Dict[str, Any]:
    """
    Create hourly analytics snapshot.
    Aggregates prediction statistics.
    """
    from app.core.database import SessionLocal
    from app.models.prediction import Prediction, AnalyticsSnapshot
    from sqlalchemy import func
    
    db = SessionLocal()
    try:
        # Get stats for the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        stats = db.query(
            func.count(Prediction.id).label("total"),
            func.sum(func.cast(Prediction.sentiment == "positive", db.Integer)).label("positive"),
            func.sum(func.cast(Prediction.sentiment == "negative", db.Integer)).label("negative"),
            func.sum(func.cast(Prediction.sentiment == "neutral", db.Integer)).label("neutral"),
            func.avg(Prediction.confidence).label("avg_confidence"),
            func.avg(Prediction.processing_time_ms).label("avg_time")
        ).filter(Prediction.created_at >= one_hour_ago).first()
        
        if stats and stats.total > 0:
            snapshot = AnalyticsSnapshot(
                date=datetime.utcnow(),
                total_predictions=stats.total or 0,
                positive_count=stats.positive or 0,
                negative_count=stats.negative or 0,
                neutral_count=stats.neutral or 0,
                avg_confidence=stats.avg_confidence,
                avg_processing_time_ms=stats.avg_time
            )
            db.add(snapshot)
            db.commit()
            
            return {"status": "created", "total": stats.total}
        
        return {"status": "skipped", "reason": "no predictions in last hour"}
        
    finally:
        db.close()


@celery_app.task
def retrain_model(model_type: str = "logistic_regression") -> Dict[str, Any]:
    """
    Trigger model retraining.
    Called when drift is detected or manually triggered.
    """
    from ml.train import train_model
    
    try:
        result = train_model(model_type=model_type)
        return {
            "status": "success",
            "model_path": result.get("model_path"),
            "metrics": result.get("metrics")
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

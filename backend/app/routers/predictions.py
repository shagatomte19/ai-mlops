"""
Predictions Router - Sentiment analysis endpoints.
Includes rate limiting and optional authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import csv
import io
import json
import time

from slowapi import Limiter
from slowapi.util import get_remote_address

from ..core.database import get_db
from ..core.config import settings
from ..core.logging import logger
from ..core.validators import sanitize_text
from ..core.cache import get_cache_service
from ..core.metrics import PREDICTION_COUNTER, PREDICTION_LATENCY, CACHE_HITS, CACHE_MISSES
from ..services.ml_service import get_ml_service, MLService
from ..services.prediction_service import get_prediction_service
from ..models.schemas import (
    PredictionRequest, PredictionResponse, 
    BatchPredictionRequest, BatchPredictionResponse,
    ExportRequest, SentimentType
)
from ..models.user import User
from ..dependencies import get_current_user_optional

router = APIRouter(prefix="/predictions", tags=["Predictions"])

# Get limiter from app state
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=PredictionResponse)
@limiter.limit(settings.RATE_LIMIT_AUTHENTICATED)
async def predict_sentiment(
    request: Request,  # Required for rate limiter - must be named 'request'
    prediction_data: PredictionRequest,
    db: Session = Depends(get_db),
    ml: MLService = Depends(get_ml_service),
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Analyze sentiment of provided text.
    
    Returns sentiment classification (positive/negative/neutral) with confidence scores.
    
    - **Rate Limited**: 100 requests/minute for authenticated users, 10/minute for anonymous
    - **Authentication**: Optional (works for both authenticated and anonymous users)
    - **Caching**: Results are cached in Redis for 1 hour
    """
    if not ml.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded. Please ensure model is trained and available."
        )
    
    try:
        # Sanitize input text
        clean_text = sanitize_text(prediction_data.text)
        
        # Check cache
        cache = get_cache_service()
        if cache.enabled:
            import hashlib
            text_hash = hashlib.md5(clean_text.encode('utf-8')).hexdigest()
            cache_key = f"prediction:{text_hash}:{ml.model_version}"
            
            cached_result = await cache.get(cache_key)
            if cached_result:
                # Add cache hit header/info if needed
                logger.debug(f"Cache hit for: {clean_text[:20]}...")
                CACHE_HITS.inc()
                return PredictionResponse(**cached_result)
            
            CACHE_MISSES.inc()
        
        # Measure latency
        with PREDICTION_LATENCY.labels(model_version=ml.model_version).time():
            # Perform prediction
            sentiment, confidence, pos_score, neg_score, neutral_score, proc_time = ml.predict(clean_text)
        
        # Increment counter
        PREDICTION_COUNTER.labels(sentiment=sentiment, model_version=ml.model_version).inc()
        
        # Store in database
        service = get_prediction_service(db)
        prediction = service.create_prediction(
            text=clean_text,
            sentiment=sentiment,
            confidence=confidence,
            positive_score=pos_score,
            negative_score=neg_score,
            neutral_score=neutral_score,
            model_version=ml.model_version,
            processing_time_ms=proc_time
        )
        
        # Prepare response
        response = PredictionResponse(
            id=prediction.id,
            sentiment=SentimentType(sentiment),
            confidence=confidence,
            positive_score=pos_score,
            negative_score=neg_score,
            neutral_score=neutral_score,
            model_version=ml.model_version,
            processing_time_ms=proc_time,
            timestamp=prediction.created_at
        )
        
        # Save to cache
        if cache.enabled:
            await cache.set(cache_key, response.model_dump(), expire=settings.CACHE_TTL_SECONDS)
        
        user_info = f" (user: {current_user.email})" if current_user else ""
        logger.info(f"Prediction: {sentiment} ({confidence:.2%}) in {proc_time:.1f}ms{user_info}")
        
        return response
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")





@router.post("/batch", response_model=BatchPredictionResponse)
async def predict_batch(
    request: BatchPredictionRequest,
    db: Session = Depends(get_db),
    ml: MLService = Depends(get_ml_service)
):
    """
    Analyze sentiment for multiple texts at once.
    
    Maximum 100 texts per request.
    """
    if not ml.is_loaded:
        raise HTTPException(status_code=503, detail="ML model not loaded")
    
    start_time = time.time()
    results = []
    service = get_prediction_service(db)
    
    for text in request.texts:
        try:
            sentiment, confidence, pos_score, neg_score, neutral_score, proc_time = ml.predict(text)
            
            prediction = service.create_prediction(
                text=text,
                sentiment=sentiment,
                confidence=confidence,
                positive_score=pos_score,
                negative_score=neg_score,
                neutral_score=neutral_score,
                model_version=ml.model_version,
                processing_time_ms=proc_time
            )
            
            results.append(PredictionResponse(
                id=prediction.id,
                sentiment=SentimentType(sentiment),
                confidence=confidence,
                positive_score=pos_score,
                negative_score=neg_score,
                neutral_score=neutral_score,
                model_version=ml.model_version,
                processing_time_ms=proc_time,
                timestamp=prediction.created_at
            ))
        except Exception as e:
            logger.warning(f"Failed to process text: {e}")
            continue
    
    total_time = (time.time() - start_time) * 1000
    
    return BatchPredictionResponse(
        results=results,
        total_processed=len(results),
        total_time_ms=total_time
    )


@router.post("/upload")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    ml: MLService = Depends(get_ml_service)
):
    """
    Upload CSV file for batch analysis.
    
    CSV must have a 'text' column.
    """
    if not ml.is_loaded:
        raise HTTPException(status_code=503, detail="ML model not loaded")
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        content = await file.read()
        decoded = content.decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))
        
        if 'text' not in reader.fieldnames:
            raise HTTPException(status_code=400, detail="CSV must have a 'text' column")
        
        texts = [row['text'] for row in reader if row.get('text', '').strip()]
        
        if len(texts) > 500:
            raise HTTPException(status_code=400, detail="Maximum 500 rows allowed")
        
        # Process batch
        request = BatchPredictionRequest(texts=texts)
        return await predict_batch(request, db, ml)
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")
    except Exception as e:
        logger.error(f"CSV upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/export")
async def export_predictions(
    start_date: datetime = None,
    end_date: datetime = None,
    sentiment: str = None,
    format: str = "json",
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    """
    Export prediction history.
    
    Supports JSON and CSV formats.
    """
    service = get_prediction_service(db)
    
    predictions = service.export_predictions(
        start_date=start_date,
        end_date=end_date,
        sentiment_filter=sentiment,
        limit=min(limit, 10000)
    )
    
    if format == "csv":
        output = io.StringIO()
        if predictions:
            writer = csv.DictWriter(output, fieldnames=predictions[0].keys())
            writer.writeheader()
            writer.writerows(predictions)
        
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode()),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=predictions.csv"}
        )
    
    return {"predictions": predictions, "count": len(predictions)}


@router.get("/{prediction_id}", response_model=PredictionResponse)
async def get_prediction(
    prediction_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific prediction by ID.
    """
    service = get_prediction_service(db)
    prediction = service.get_prediction(prediction_id)
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return PredictionResponse(
        id=prediction.id,
        sentiment=SentimentType(prediction.sentiment),
        confidence=prediction.confidence,
        positive_score=prediction.positive_score,
        negative_score=prediction.negative_score,
        neutral_score=prediction.neutral_score or 0.0,
        model_version=prediction.model_version,
        processing_time_ms=prediction.processing_time_ms,
        timestamp=prediction.created_at
    )

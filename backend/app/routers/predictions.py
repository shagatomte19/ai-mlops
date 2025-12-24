"""
Predictions Router - Sentiment analysis endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import csv
import io
import json
import time

from ..core.database import get_db
from ..core.config import settings
from ..core.logging import logger
from ..services.ml_service import get_ml_service, MLService
from ..services.prediction_service import get_prediction_service
from ..models.schemas import (
    PredictionRequest, PredictionResponse, 
    BatchPredictionRequest, BatchPredictionResponse,
    ExportRequest, SentimentType
)

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("", response_model=PredictionResponse)
async def predict_sentiment(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    ml: MLService = Depends(get_ml_service)
):
    """
    Analyze sentiment of provided text.
    
    Returns sentiment classification (positive/negative/neutral) with confidence scores.
    """
    if not ml.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="ML model not loaded. Please ensure model is trained and available."
        )
    
    try:
        # Perform prediction
        sentiment, confidence, pos_score, neg_score, neutral_score, proc_time = ml.predict(request.text)
        
        # Store in database
        service = get_prediction_service(db)
        prediction = service.create_prediction(
            text=request.text,
            sentiment=sentiment,
            confidence=confidence,
            positive_score=pos_score,
            negative_score=neg_score,
            neutral_score=neutral_score,
            model_version=ml.model_version,
            processing_time_ms=proc_time
        )
        
        logger.info(f"Prediction: {sentiment} ({confidence:.2%}) in {proc_time:.1f}ms")
        
        return PredictionResponse(
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

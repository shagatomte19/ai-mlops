"""
Machine Learning Service for sentiment prediction.
Handles model loading, inference, and preprocessing.
"""
import joblib
import os
import time
from typing import Optional, Tuple, List
from pathlib import Path

from ..core.config import settings
from ..core.logging import logger


class MLService:
    """Service for ML model operations."""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.model_version = settings.MODEL_VERSION
        self._loaded = False
    
    def load_models(self) -> bool:
        """Load ML model and vectorizer from disk."""
        try:
            # Try new paths first, fallback to legacy paths
            model_paths = [
                settings.MODEL_PATH,
                "ml/models/sentiment_v2.pkl",
                "sentiment_v1.pkl",
                "../sentiment_v1.pkl",
            ]
            vectorizer_paths = [
                settings.VECTORIZER_PATH,
                "ml/models/vectorizer_v2.pkl",
                "vectorizer_v1.pkl",
                "../vectorizer_v1.pkl",
            ]
            
            model_loaded = False
            vectorizer_loaded = False
            
            for path in model_paths:
                if os.path.exists(path):
                    self.model = joblib.load(path)
                    logger.info(f"Model loaded from: {path}")
                    model_loaded = True
                    break
            
            for path in vectorizer_paths:
                if os.path.exists(path):
                    self.vectorizer = joblib.load(path)
                    logger.info(f"Vectorizer loaded from: {path}")
                    vectorizer_loaded = True
                    break
            
            self._loaded = model_loaded and vectorizer_loaded
            
            if not self._loaded:
                logger.warning("Model files not found. Train model first using: python -m ml.train")
            
            return self._loaded
            
        except Exception as e:
            logger.error(f"Failed to load models: {e}")
            return False
    
    @property
    def is_loaded(self) -> bool:
        """Check if models are loaded."""
        return self._loaded and self.model is not None and self.vectorizer is not None
    
    def preprocess_text(self, text: str) -> str:
        """Preprocess input text."""
        # Basic preprocessing - can be extended
        text = text.strip()
        # Remove excessive whitespace
        text = ' '.join(text.split())
        return text
    
    def predict(self, text: str) -> Tuple[str, float, float, float, float, float]:
        """
        Perform sentiment prediction on text.
        
        Returns:
            Tuple of (sentiment, confidence, positive_score, negative_score, neutral_score, processing_time_ms)
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded")
        
        start_time = time.time()
        
        # Preprocess
        processed_text = self.preprocess_text(text)
        
        # Vectorize
        text_vector = self.vectorizer.transform([processed_text])
        
        # Predict
        prediction = self.model.predict(text_vector)[0]
        probabilities = self.model.predict_proba(text_vector)[0]
        
        # Extract scores (assuming binary classification: [negative, positive])
        negative_score = float(probabilities[0])
        positive_score = float(probabilities[1])
        
        # Determine sentiment with neutral detection via confidence threshold
        confidence = max(positive_score, negative_score)
        neutral_threshold = 0.6  # If confidence < 60%, consider neutral
        
        if confidence < neutral_threshold:
            sentiment = "neutral"
            neutral_score = 1.0 - confidence
        else:
            sentiment = "positive" if prediction == 1 else "negative"
            neutral_score = 0.0
        
        processing_time_ms = (time.time() - start_time) * 1000
        
        return sentiment, confidence, positive_score, negative_score, neutral_score, processing_time_ms
    
    def predict_batch(self, texts: List[str]) -> List[Tuple[str, float, float, float, float, float]]:
        """
        Perform batch sentiment predictions.
        
        Returns:
            List of prediction tuples
        """
        if not self.is_loaded:
            raise RuntimeError("Models not loaded")
        
        results = []
        for text in texts:
            result = self.predict(text)
            results.append(result)
        
        return results
    
    def get_model_info(self) -> dict:
        """Get information about the loaded model."""
        return {
            "version": self.model_version,
            "loaded": self._loaded,
            "model_type": type(self.model).__name__ if self.model else None,
            "vectorizer_type": type(self.vectorizer).__name__ if self.vectorizer else None,
        }


# Singleton instance
ml_service = MLService()


def get_ml_service() -> MLService:
    """Dependency for getting ML service."""
    return ml_service

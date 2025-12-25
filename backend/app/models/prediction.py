"""
SQLAlchemy ORM Models for the Sentiment Analysis application.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from datetime import datetime

from ..core.database import Base


class Prediction(Base):
    """Model for storing sentiment prediction results."""
    
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    text = Column(Text, nullable=False)
    sentiment = Column(String(20), nullable=False, index=True)  # positive, negative, neutral
    confidence = Column(Float, nullable=False)
    positive_score = Column(Float, nullable=False)
    negative_score = Column(Float, nullable=False)
    neutral_score = Column(Float, nullable=True, default=0.0)
    model_version = Column(String(20), nullable=True, default="v1.0")
    processing_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    def __repr__(self):
        return f"<Prediction(id={self.id}, sentiment='{self.sentiment}', confidence={self.confidence:.2f})>"
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "text": self.text,
            "sentiment": self.sentiment,
            "confidence": self.confidence,
            "positive_score": self.positive_score,
            "negative_score": self.negative_score,
            "neutral_score": self.neutral_score,
            "model_version": self.model_version,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.created_at.isoformat() if self.created_at else None,
        }


class ModelVersion(Base):
    """Model for tracking ML model versions and their metrics."""
    
    __tablename__ = "model_versions"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    version = Column(String(20), unique=True, nullable=False)
    accuracy = Column(Float, nullable=True)
    precision = Column(Float, nullable=True)
    recall = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    training_samples = Column(Integer, nullable=True)
    model_path = Column(String(255), nullable=True)
    vectorizer_path = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=False)
    model_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<ModelVersion(version='{self.version}', accuracy={self.accuracy:.4f})>"


class AnalyticsSnapshot(Base):
    """Model for storing daily analytics snapshots."""
    
    __tablename__ = "analytics_snapshots"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    total_predictions = Column(Integer, default=0)
    positive_count = Column(Integer, default=0)
    negative_count = Column(Integer, default=0)
    neutral_count = Column(Integer, default=0)
    avg_confidence = Column(Float, nullable=True)
    avg_processing_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AnalyticsSnapshot(date={self.date}, total={self.total_predictions})>"

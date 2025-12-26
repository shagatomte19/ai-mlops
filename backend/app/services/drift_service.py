"""
Drift Detection Service using Evidently.
Monitors data drift and model performance degradation.
"""
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from evidently import Report
from evidently.presets import DataDriftPreset

from ..core.config import settings
from ..core.logging import logger
from ..models.prediction import Prediction
from ..services.ml_service import ml_service


class DriftService:
    """Service for detecting data and concept drift."""
    
    def __init__(self):
        self.reference_data_path = "ml/data/sentiment_dataset_v2.csv"
        self._reference_data = None
        self.reports_dir = "ml/reports"
        
        os.makedirs(self.reports_dir, exist_ok=True)
        
    @property
    def reference_data(self) -> pd.DataFrame:
        """Load and cache reference (training) data."""
        if self._reference_data is None:
            try:
                if os.path.exists(self.reference_data_path):
                    df = pd.read_csv(self.reference_data_path)
                    # Keep only relevant columns
                    if 'text' in df.columns and 'sentiment' in df.columns:
                        self._reference_data = df[['text', 'sentiment']]
                    else:
                        logger.warning("Reference data missing required columns")
                else:
                    logger.warning(f"Reference data not found at {self.reference_data_path}")
            except Exception as e:
                logger.error(f"Failed to load reference data: {e}")
        
        return self._reference_data

    def get_production_data(self, db: Session, days: int = 7) -> pd.DataFrame:
        """Fetch recent production predictions from database."""
        since = datetime.now() - timedelta(days=days)
        
        query = db.query(Prediction).filter(Prediction.created_at >= since)
        predictions = query.all()
        
        if not predictions:
            return pd.DataFrame()
        
        data = [
            {
                "text": p.text,
                "prediction": p.sentiment,
                "confidence": p.confidence
            }
            for p in predictions
        ]
        
        return pd.DataFrame(data)

    def detect_drift(self, db: Session, days: int = 7) -> Dict[str, Any]:
        """
        Run drift detection comparing recent production data vs reference data.
        
        Returns:
            Dictionary containing drift metrics and status.
        """
        current_data = self.get_production_data(db, days)
        reference_data = self.reference_data
        
        if reference_data is None or current_data.empty:
            return {
                "status": "error",
                "message": "Insufficient data for drift detection",
                "drift_detected": False
            }
        
        if len(current_data) < 10:
             return {
                "status": "skipped",
                "message": "Not enough production data (min 10 samples)",
                "drift_detected": False
            }
            
        # Prepare data for Evidently
        # Rename columns if necessary to match reference
        current_data['sentiment'] = current_data['prediction']  # evidently expects target/prediction columns
        
        # Create report
        report = Report(metrics=[
            DataDriftPreset()
        ])
        
        try:
            report.run(
                reference_data=reference_data,
                current_data=current_data,
                column_mapping=None  # evidently auto-detects
            )
            
            # Save report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_path = os.path.join(self.reports_dir, f"drift_report_{timestamp}.json")
            report.save_json(report_path)
            
            # Parse results
            results = report.as_dict()
            drift_share = results['metrics'][1]['result']['drift_share']
            drift_detected = results['metrics'][1]['result']['dataset_drift']
            
            logger.info(f"Drift analysis complete. Drift detected: {drift_detected} (share: {drift_share:.2f})")
            
            return {
                "status": "success",
                "drift_detected": drift_detected,
                "drift_share": drift_share,
                "report_path": report_path,
                "analyzed_samples": len(current_data),
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Drift detection failed: {e}")
            return {
                "status": "error",
                "message": str(e),
                "drift_detected": False
            }


drift_service = DriftService()


def get_drift_service() -> DriftService:
    return drift_service

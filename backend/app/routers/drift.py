"""
Drift Analysis Router.
Endpoints for triggering and retrieving drift analysis reports.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any, List

from ..core.database import get_db
from ..core.logging import logger
from ..services.drift_service import get_drift_service, DriftService
from ..models.user import User
from ..dependencies import get_current_admin_user

router = APIRouter(prefix="/drift", tags=["MLOps - Drift Detection"])


@router.post("/analyze", response_model=Dict[str, Any])
async def trigger_drift_analysis(
    days: int = 7,
    db: Session = Depends(get_db),
    service: DriftService = Depends(get_drift_service),
    current_user: User = Depends(get_current_admin_user)
):
    """
    Trigger a new data drift analysis.
    Compares the last N days of production data against the training dataset.
    
    Requires Admin privileges.
    """
    try:
        result = service.detect_drift(db, days)
        return result
    except Exception as e:
        logger.error(f"Drift analysis endpoints failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/reports", response_model=List[str])
async def list_reports(
    service: DriftService = Depends(get_drift_service),
    current_user: User = Depends(get_current_admin_user)
):
    """
    List available drift reports.
    """
    import os
    try:
        reports = sorted(os.listdir(service.reports_dir), reverse=True)
        return reports
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

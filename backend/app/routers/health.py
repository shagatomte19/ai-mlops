"""
Health Check Router - System health and status endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import time

from ..core.database import get_db
from ..core.config import settings
from ..services.ml_service import get_ml_service, MLService
from ..models.schemas import HealthResponse, ModelInfoResponse

router = APIRouter(prefix="/health", tags=["Health"])

# Track startup time
_start_time = time.time()


@router.get("", response_model=HealthResponse)
async def health_check(
    db: Session = Depends(get_db),
    ml: MLService = Depends(get_ml_service)
):
    """
    System health check endpoint.
    Returns status of all system components.
    """
    # Check database connection
    db_connected = False
    try:
        db.execute(text("SELECT 1"))
        db_connected = True
    except Exception:
        pass
    
    return HealthResponse(
        status="healthy" if (db_connected and ml.is_loaded) else "degraded",
        version=settings.APP_VERSION,
        model_loaded=ml.is_loaded,
        database_connected=db_connected,
        uptime_seconds=time.time() - _start_time
    )


@router.get("/model", response_model=ModelInfoResponse)
async def model_info(ml: MLService = Depends(get_ml_service)):
    """
    Get information about the loaded ML model.
    """
    info = ml.get_model_info()
    return ModelInfoResponse(
        version=info["version"],
        is_active=info["loaded"]
    )


@router.get("/ready")
async def readiness_check(
    db: Session = Depends(get_db),
    ml: MLService = Depends(get_ml_service)
):
    """
    Kubernetes-style readiness probe.
    """
    try:
        db.execute(text("SELECT 1"))
        if ml.is_loaded:
            return {"ready": True}
    except Exception:
        pass
    
    return {"ready": False}


@router.get("/live")
async def liveness_check():
    """
    Kubernetes-style liveness probe.
    """
    return {"alive": True}

```
"""
Health Check Router - System health and status endpoints.
"""
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..core.database import get_db
from ..core.cache import get_cache_service
from ..services.ml_service import get_ml_service, MLService
from ..models.schemas import ModelInfoResponse

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic container health check."""
    return {"status": "ok"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(
    db: Session = Depends(get_db),
    ml: MLService = Depends(get_ml_service)
) -> Dict[str, Any]:
    """
    Readiness probe with component status checks.
    Checks: Database, Redis, ML Model.
    """
    status_report = {
        "status": "ready",
        "components": {
            "database": "unknown",
            "redis": "unknown",
            "ml_model": "unknown"
        }
    }
    
    # Check Database
    try:
        db.execute(text("SELECT 1"))
        status_report["components"]["database"] = "up"
    except Exception as e:
        status_report["components"]["database"] = f"down: {str(e)}"
        status_report["status"] = "not_ready"

    # Check Redis
    try:
        cache = get_cache_service()
        if cache.enabled:
            # Simple set/get check or ping
            if await cache.set("health_check", "ok", expire=5):
                status_report["components"]["redis"] = "up"
            else:
                status_report["components"]["redis"] = "error"
        else:
            status_report["components"]["redis"] = "disabled"
    except Exception as e:
        status_report["components"]["redis"] = f"down: {str(e)}"
        # Redis optional, don't fail readiness? Or fail if critical?
        # Assuming optional for now

    # Check ML Model
    if ml.is_loaded:
        status_report["components"]["ml_model"] = "up"
    else:
        status_report["components"]["ml_model"] = "down"
        status_report["status"] = "not_ready"

    if status_report["status"] != "ready":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=status_report
        )
        
    return status_report


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

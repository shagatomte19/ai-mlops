"""
Scheduler Service using APScheduler.
Handles background tasks like drift detection and automated retraining.
"""
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from ..core.database import SessionLocal
from ..core.logging import logger
from ..services.drift_service import get_drift_service
from ..services.ml_service import ml_service
# Import train_model indirectly to avoid top-level script execution issues
import ml.train

scheduler = AsyncIOScheduler()


async def check_drift_and_retrain():
    """
    Scheduled task to check for data drift and retrain model if needed.
    """
    logger.info("Running scheduled drift check...")
    db = SessionLocal()
    try:
        drift_service = get_drift_service()
        # Check drift for last 7 days
        result = drift_service.detect_drift(db, days=7)
        
        if result.get("drift_detected", False):
            logger.warning(f"Drift detected (share: {result.get('drift_share', 0):.2f})! Initiating retraining...")
            
            # Run training in thread executor to avoid blocking the event loop
            loop = asyncio.get_event_loop()
            # Default to logistic regression for automated retraining
            train_result = await loop.run_in_executor(
                None, 
                ml.train.train_model, 
                "logistic_regression"
            )
            
            logger.info(f"Model retrained. New version: {train_result.get('version')}")
            
            # Reload model in the service
            ml_service.load_models()
            logger.info("Model reloaded successfully.")
            
        else:
            logger.info("No significant drift detected. Skipping retraining.")
            
    except Exception as e:
        logger.error(f"Scheduled task failed: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the background scheduler."""
    # Run once shortly after startup for demonstration/testing (optional)
    # scheduler.add_job(check_drift_and_retrain, 'date', run_date=datetime.now() + timedelta(minutes=1))
    
    # Schedule daily check
    scheduler.add_job(
        check_drift_and_retrain,
        IntervalTrigger(hours=24),
        id="drift_check",
        replace_existing=True
    )
    scheduler.start()
    logger.info("Background scheduler started")


async def stop_scheduler():
    """Stop the scheduler."""
    scheduler.shutdown()
    logger.info("Scheduler stopped")

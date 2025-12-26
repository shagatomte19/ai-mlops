"""
Celery Application Configuration.
Handles async background task processing.
"""
import os
from celery import Celery

# Get Redis URL from environment or use default
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Create Celery app
celery_app = Celery(
    "sentimentai",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.tasks.prediction_tasks"]
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task execution settings
    task_soft_time_limit=300,  # 5 minutes soft limit
    task_time_limit=600,       # 10 minutes hard limit
    
    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,
    
    # Result backend settings
    result_expires=3600,  # Results expire after 1 hour
    
    # Task routing
    task_routes={
        "app.tasks.prediction_tasks.*": {"queue": "predictions"},
        "app.tasks.training_tasks.*": {"queue": "training"},
    },
    
    # Default queue
    task_default_queue="default",
    
    # Beat scheduler for periodic tasks
    beat_schedule={
        "daily-drift-check": {
            "task": "app.tasks.prediction_tasks.check_drift",
            "schedule": 86400.0,  # Every 24 hours
        },
        "hourly-analytics-snapshot": {
            "task": "app.tasks.prediction_tasks.create_analytics_snapshot",
            "schedule": 3600.0,  # Every hour
        },
    },
)

# Optional: Configure task annotations for rate limiting
celery_app.conf.task_annotations = {
    "app.tasks.prediction_tasks.process_batch": {
        "rate_limit": "10/m"  # Max 10 batch tasks per minute
    }
}

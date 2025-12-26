"""
SentimentAI - Production-Grade Sentiment Analysis API
Main application entry point with FastAPI configuration.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

# Rate limiting imports
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Prometheus metrics
from prometheus_fastapi_instrumentator import Instrumentator

from .core.config import settings
from .core.database import init_db
from .core.logging import setup_logging, logger
from .core.cache import cache_service
from .services.ml_service import ml_service
from .services.scheduler import start_scheduler, stop_scheduler
from .routers import health, predictions, stats, auth, drift


# Rate limiter with remote address as key
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - startup and shutdown events."""
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Load ML models
    if ml_service.load_models():
        logger.info("ML models loaded successfully")
    else:
        logger.warning("ML models not loaded - predictions will fail")
    
    # Start scheduler
    start_scheduler()
    
    yield
    
    # Shutdown
    await stop_scheduler()
    await cache_service.close()
    logger.info("Cache connection closed")
    logger.info("Application shutting down")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    🎯 **SentimentAI** - Advanced Sentiment Analysis API
    
    A production-grade machine learning service for real-time sentiment analysis.
    
    ## Features
    - ✅ Single text analysis with confidence scores
    - ✅ Batch processing for multiple texts
    - ✅ CSV file upload support
    - ✅ Analytics dashboard data
    - ✅ Trend analysis and visualization data
    - ✅ Export functionality (JSON/CSV)
    - ✅ JWT Authentication
    - ✅ Rate Limiting
    - ✅ Redis Caching
    - ✅ Drift Detection (MLOps)
    
    ## Authentication
    Most endpoints require JWT authentication. Get a token via `/api/v1/auth/login`.
    
    ## Sentiment Classes
    - **Positive**: High confidence positive sentiment
    - **Negative**: High confidence negative sentiment  
    - **Neutral**: Low confidence or ambiguous sentiment
    """,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter

# Rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__}
    )


# Prometheus metrics instrumentation
Instrumentator().instrument(app).expose(app, endpoint="/metrics")


# Register routers with API versioning
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(health.router, prefix=settings.API_V1_PREFIX)
app.include_router(predictions.router, prefix=settings.API_V1_PREFIX)
app.include_router(stats.router, prefix=settings.API_V1_PREFIX)
app.include_router(drift.router, prefix=settings.API_V1_PREFIX)



# Legacy endpoints for backward compatibility
@app.get("/api/health")
async def legacy_health():
    """Legacy health endpoint - redirects to v1."""
    return {"status": "ok", "message": "Use /api/v1/health for full status"}


@app.post("/api/predict")
async def legacy_predict(request: dict):
    """Legacy predict endpoint notice."""
    return {"error": "This endpoint has moved to /api/v1/predictions"}


@app.get("/api/stats")
async def legacy_stats():
    """Legacy stats endpoint notice."""
    return {"error": "This endpoint has moved to /api/v1/stats"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "auth": f"{settings.API_V1_PREFIX}/auth",
        "predict": f"{settings.API_V1_PREFIX}/predictions",
        "stats": f"{settings.API_V1_PREFIX}/stats",
        "metrics": "/metrics",
    }


"""
Structured logging configuration using loguru.
Provides colorful console output and file logging.
"""
import sys
from loguru import logger
from .config import settings


def setup_logging() -> None:
    """Configure application logging."""
    
    # Remove default handler
    logger.remove()
    
    # Console handler with colors
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stderr,
        format=log_format,
        level="DEBUG" if settings.DEBUG else "INFO",
        colorize=True,
    )
    
    # File handler for production
    if not settings.DEBUG:
        logger.add(
            "logs/app.log",
            rotation="10 MB",
            retention="7 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            level="INFO",
        )
    
    logger.info(f"Logging configured - Debug mode: {settings.DEBUG}")


# Export logger for use in other modules
__all__ = ["logger", "setup_logging"]

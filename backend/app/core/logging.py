"""
Structured logging configuration using loguru.
Provides colorful console output for dev and JSON output for production.
Intercepts standard library logging (uvicorn, fastapi) to unify logs.
"""
import sys
import logging
from loguru import logger
from .config import settings


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentation.
    Intercepts standard logging messages and redirects them to loguru.
    """
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def setup_logging() -> None:
    """Configure application logging."""
    
    # Remove default handler
    logger.remove()
    
    # Define handlers
    if settings.DEBUG:
        # Development: Colorful console output
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            level="DEBUG",
            colorize=True,
        )
    else:
        # Production: JSON output
        logger.add(
            sys.stderr,
            serialize=True,
            level="INFO",
        )
        
        # Also log to file in JSON
        logger.add(
            "logs/app.json",
            rotation="10 MB",
            retention="7 days",
            serialize=True,
            level="INFO",
        )
    
    # Intercept standard logging (uvicorn, fastapi, sqlalchemy)
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # Explicitly set levels for some loggers to avoid noise
    logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]
    logging.getLogger("uvicorn.error").handlers = [InterceptHandler()]
    
    for name in logging.root.manager.loggerDict:
        if name.startswith("uvicorn"):
            logging.getLogger(name).handlers = []
            
    logger.info(f"Logging configured - Debug mode: {settings.DEBUG}")


# Export logger for use in other modules
__all__ = ["logger", "setup_logging"]

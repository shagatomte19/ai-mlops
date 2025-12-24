"""
Database configuration with SQLAlchemy and Supabase PostgreSQL support.
Provides async session management and connection pooling.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Generator
import os

from .config import settings


# SQLAlchemy Base for models
Base = declarative_base()


def get_database_url() -> str:
    """Get database URL from settings or fallback to SQLite."""
    if settings.DATABASE_URL:
        # Supabase PostgreSQL
        return settings.DATABASE_URL
    else:
        # Fallback to SQLite for local development
        return "sqlite:///./sentiment.db"


# Create engine with appropriate settings
database_url = get_database_url()

if database_url.startswith("sqlite"):
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        echo=settings.DEBUG
    )
else:
    # PostgreSQL with connection pooling
    engine = create_engine(
        database_url,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=settings.DEBUG
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for getting database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    """Context manager for database sessions."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized: {database_url.split('@')[-1] if '@' in database_url else database_url}")

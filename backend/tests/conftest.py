"""
Pytest configuration and fixtures for testing.
"""
import os
import pytest
from typing import Generator, Dict, Any
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Set test environment before importing app
os.environ["DEBUG"] = "true"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User
from app.core.security import get_password_hash, create_access_token


# Test database URL - use SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="session")
def engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """Create a fresh database session for each test."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Create a test client with database override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db_session: Session) -> User:
    """Create a test user in the database."""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("TestPassword123!"),
        full_name="Test User",
        is_active=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(test_user: User) -> Dict[str, str]:
    """Generate authentication headers for test user."""
    token = create_access_token(subject=test_user.email)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_user(db_session: Session) -> User:
    """Create an admin user in the database."""
    user = User(
        email="admin@example.com",
        hashed_password=get_password_hash("AdminPassword123!"),
        full_name="Admin User",
        is_active=True,
        is_admin=True,
        is_verified=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def admin_headers(admin_user: User) -> Dict[str, str]:
    """Generate authentication headers for admin user."""
    token = create_access_token(subject=admin_user.email)
    return {"Authorization": f"Bearer {token}"}

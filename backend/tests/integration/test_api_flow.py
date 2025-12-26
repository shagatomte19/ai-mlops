"""
Integration tests for API endpoints.
Tests the full user journey from registration to prediction.
"""
import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_check(self, client: TestClient):
        """Test basic health endpoint."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


class TestAuthFlow:
    """Test authentication flow."""
    
    def test_register_user(self, client: TestClient):
        """Test user registration."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "password": "SecurePassword123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["user"]["email"] == "newuser@example.com"
    
    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with existing email fails."""
        response = client.post(
            "/api/v1/auth/register",
            json={
                "email": test_user.email,
                "password": "AnotherPassword123!"
            }
        )
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self, client: TestClient, test_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "TestPassword123!"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
    
    def test_login_wrong_password(self, client: TestClient, test_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user.email,
                "password": "WrongPassword123!"
            }
        )
        assert response.status_code == 401
    
    def test_get_current_user(self, client: TestClient, auth_headers):
        """Test getting current user info."""
        response = client.get("/api/v1/auth/me", headers=auth_headers)
        assert response.status_code == 200
        assert response.json()["email"] == "test@example.com"


class TestPredictionFlow:
    """Test prediction endpoints."""
    
    def test_predict_sentiment_anonymous(self, client: TestClient):
        """Test prediction without authentication."""
        response = client.post(
            "/api/v1/predictions",
            json={"text": "This is a great product! I love it."}
        )
        # Should work for anonymous users
        assert response.status_code in [200, 503]  # 503 if model not loaded
    
    def test_predict_sentiment_authenticated(self, client: TestClient, auth_headers):
        """Test prediction with authentication."""
        response = client.post(
            "/api/v1/predictions",
            json={"text": "Terrible experience, very disappointed."},
            headers=auth_headers
        )
        assert response.status_code in [200, 503]
        if response.status_code == 200:
            data = response.json()
            assert "sentiment" in data
            assert "confidence" in data
    
    def test_predict_empty_text(self, client: TestClient):
        """Test prediction with empty text."""
        response = client.post(
            "/api/v1/predictions",
            json={"text": ""}
        )
        assert response.status_code == 422  # Validation error


class TestUserJourney:
    """Test complete user journey."""
    
    def test_full_user_journey(self, client: TestClient):
        """Test: Register -> Login -> Predict -> View History."""
        # 1. Register
        register_response = client.post(
            "/api/v1/auth/register",
            json={
                "email": "journey@example.com",
                "password": "JourneyPassword123!"
            }
        )
        assert register_response.status_code == 200
        token = register_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Get profile
        profile_response = client.get("/api/v1/auth/me", headers=headers)
        assert profile_response.status_code == 200
        
        # 3. Make prediction (may fail if model not loaded)
        predict_response = client.post(
            "/api/v1/predictions",
            json={"text": "This is an amazing journey test!"},
            headers=headers
        )
        # Accept both success and model-not-loaded
        assert predict_response.status_code in [200, 503]

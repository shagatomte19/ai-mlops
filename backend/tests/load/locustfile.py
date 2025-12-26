"""
Load testing with Locust.
Simulates user traffic patterns for performance testing.

Run with: locust -f tests/load/locustfile.py --host=http://localhost:8000
"""
import random
from locust import HttpUser, task, between


class AnonymousUser(HttpUser):
    """Simulates anonymous user behavior."""
    
    wait_time = between(1, 3)
    weight = 3  # 3x more likely than authenticated users
    
    @task(10)
    def health_check(self):
        """Check health endpoint."""
        self.client.get("/api/v1/health")
    
    @task(5)
    def predict_sentiment(self):
        """Make a prediction request."""
        texts = [
            "This product is absolutely amazing! Best purchase ever.",
            "Terrible experience, would not recommend to anyone.",
            "It's okay, nothing special but gets the job done.",
            "Love it! Five stars without hesitation.",
            "Worst customer service I've ever encountered.",
            "Meh, could be better but also could be worse.",
        ]
        self.client.post(
            "/api/v1/predictions",
            json={"text": random.choice(texts)}
        )
    
    @task(2)
    def get_stats(self):
        """Get statistics."""
        self.client.get("/api/v1/stats/overview")


class AuthenticatedUser(HttpUser):
    """Simulates authenticated user behavior."""
    
    wait_time = between(0.5, 2)
    weight = 1
    token = None
    
    def on_start(self):
        """Login on start."""
        # Register a unique user
        email = f"loadtest_{random.randint(1, 100000)}@test.com"
        response = self.client.post(
            "/api/v1/auth/register",
            json={
                "email": email,
                "password": "LoadTestPassword123!"
            }
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            # Try login if already exists
            response = self.client.post(
                "/api/v1/auth/login",
                json={
                    "email": email,
                    "password": "LoadTestPassword123!"
                }
            )
            if response.status_code == 200:
                self.token = response.json().get("access_token")
    
    def get_headers(self):
        """Get auth headers."""
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}
    
    @task(10)
    def predict_sentiment(self):
        """Make authenticated prediction."""
        texts = [
            "Excellent quality and fast shipping!",
            "Not worth the money, very disappointed.",
            "Average product, nothing to write home about.",
        ]
        self.client.post(
            "/api/v1/predictions",
            json={"text": random.choice(texts)},
            headers=self.get_headers()
        )
    
    @task(3)
    def get_profile(self):
        """Get user profile."""
        self.client.get("/api/v1/auth/me", headers=self.get_headers())
    
    @task(2)
    def batch_predict(self):
        """Batch prediction request."""
        self.client.post(
            "/api/v1/predictions/batch",
            json={
                "texts": [
                    "Great product!",
                    "Terrible service.",
                    "Okay experience."
                ]
            },
            headers=self.get_headers()
        )

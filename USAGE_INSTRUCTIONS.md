# SentimentAI - Usage Instructions

## Table of Contents
- [Quick Start](#quick-start)
- [API Usage](#api-usage)
- [Authentication](#authentication)
- [Making Predictions](#making-predictions)
- [Batch Processing](#batch-processing)
- [Analytics](#analytics)
- [Admin Operations](#admin-operations)
- [Background Tasks](#background-tasks)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Start the Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Configure your settings
alembic upgrade head  # Run migrations
uvicorn app.main:app --reload --port 8000
```

### 2. Start the Frontend
```bash
cd sentiment-frontend
npm install
npm run dev
```

### 3. Access the Application
- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics

---

## API Usage

### Base URL
```
http://localhost:8000/api/v1
```

### Response Format
All responses are JSON with this structure:
```json
{
  "field1": "value1",
  "field2": "value2"
}
```

Errors return:
```json
{
  "detail": "Error message"
}
```

---

## Authentication

### Register a New User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGci...",
  "refresh_token": "eyJhbGci...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "is_active": true
  }
}
```

### Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

### Using the Token
Add the token to all authenticated requests:
```bash
curl -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  http://localhost:8000/api/v1/auth/me
```

### Refresh Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "YOUR_REFRESH_TOKEN"}'
```

---

## Making Predictions

### Single Text Analysis
```bash
curl -X POST http://localhost:8000/api/v1/predictions \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is absolutely amazing! Best purchase ever."}'
```

Response:
```json
{
  "id": 1,
  "sentiment": "positive",
  "confidence": 0.95,
  "positive_score": 0.95,
  "negative_score": 0.03,
  "neutral_score": 0.02,
  "model_version": "v2.0",
  "processing_time_ms": 12.5,
  "timestamp": "2024-12-26T12:00:00Z"
}
```

### Authenticated Prediction
```bash
curl -X POST http://localhost:8000/api/v1/predictions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"text": "Terrible experience, would not recommend."}'
```

---

## Batch Processing

### Batch Prediction (Multiple Texts)
```bash
curl -X POST http://localhost:8000/api/v1/predictions/batch \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "texts": [
      "Great product!",
      "Terrible service.",
      "It was okay."
    ]
  }'
```

### CSV Upload
```bash
curl -X POST http://localhost:8000/api/v1/predictions/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@reviews.csv"
```

CSV format:
```csv
text
"This is great!"
"Not happy with this."
"Average experience."
```

---

## Analytics

### Get Overview Statistics
```bash
curl http://localhost:8000/api/v1/stats/overview
```

### Get Sentiment Trends
```bash
curl "http://localhost:8000/api/v1/stats/trends?days=30"
```

### Export Data
```bash
curl -X POST http://localhost:8000/api/v1/predictions/export \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"format": "csv", "days": 7}'
```

---

## Admin Operations

### Trigger Drift Analysis (Admin Only)
```bash
curl -X POST http://localhost:8000/api/v1/drift/analyze \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

### List Drift Reports
```bash
curl http://localhost:8000/api/v1/drift/reports \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## Background Tasks

### Start Celery Worker
```bash
cd backend
celery -A app.tasks.celery_app worker --loglevel=info
```

### Start Scheduler (Beat)
```bash
celery -A app.tasks.celery_app beat --loglevel=info
```

### Manually Trigger Tasks
```bash
# Trigger retraining
celery -A app.tasks.celery_app call app.tasks.prediction_tasks.retrain_model

# Trigger drift check
celery -A app.tasks.celery_app call app.tasks.prediction_tasks.check_drift
```

---

## Monitoring

### Health Checks
```bash
# Basic health
curl http://localhost:8000/api/v1/health

# Detailed readiness
curl http://localhost:8000/api/v1/health/ready
```

### Prometheus Metrics
```bash
curl http://localhost:8000/metrics
```

Key metrics:
- `sentiment_predictions_total` - Prediction count by sentiment
- `prediction_processing_seconds` - Latency histogram
- `cache_hits_total` / `cache_misses_total` - Cache performance

---

## Troubleshooting

### Model Not Loaded
```bash
# Train a new model
cd backend
python -m ml.train --model logistic_regression
```

### Database Connection Failed
```bash
# Check DATABASE_URL in .env
# Verify PostgreSQL is running
psql $DATABASE_URL -c "SELECT 1"
```

### Rate Limited (429 Error)
- Anonymous: 10 requests/minute
- Authenticated: 100 requests/minute
- Wait and retry, or authenticate for higher limits

### Token Expired (401 Error)
- Access tokens expire in 30 minutes
- Use refresh token to get new access token
- Or login again

---

## Rate Limits

| User Type | Limit |
|-----------|-------|
| Anonymous | 10/min |
| Authenticated | 100/min |
| Batch | 5/hour |

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | SQLite fallback |
| `SECRET_KEY` | JWT signing key | Auto-generated |
| `REDIS_URL` | Redis connection for caching | Disabled |
| `DEBUG` | Enable debug mode | `false` |
| `CORS_ORIGINS` | Allowed origins | `["*"]` |

---

For more information, see the [API Documentation](http://localhost:8000/docs).

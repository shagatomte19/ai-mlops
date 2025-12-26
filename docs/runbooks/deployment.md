# Deployment Runbook

## Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+ (optional but recommended)

---

## Local Development

### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup
```bash
cd sentiment-frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## Production Deployment

### Environment Variables
```bash
# Required
DATABASE_URL=postgresql://user:pass@host:5432/db
SECRET_KEY=your-256-bit-secret-key

# Optional but recommended
REDIS_URL=redis://localhost:6379/0
DEBUG=false
CORS_ORIGINS=["https://yourdomain.com"]
```

### Deploy Backend
```bash
# Install production dependencies
pip install -r requirements.txt gunicorn

# Run migrations
alembic upgrade head

# Train model (if not exists)
python -m ml.train --model logistic_regression

# Start with Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000
```

### Deploy Frontend
```bash
cd sentiment-frontend

# Build production bundle
npm run build

# Serve with nginx or any static server
# Copy dist/ contents to your web server
```

### Start Background Workers
```bash
# Celery worker
celery -A app.tasks.celery_app worker --loglevel=info --concurrency=4

# Celery beat (scheduler)
celery -A app.tasks.celery_app beat --loglevel=info
```

---

## Health Checks

### Endpoints
- `GET /api/v1/health` - Basic liveness
- `GET /api/v1/health/ready` - Full readiness (DB, Redis, Model)
- `GET /metrics` - Prometheus metrics

### Verify Deployment
```bash
# Check health
curl http://localhost:8000/api/v1/health

# Check readiness
curl http://localhost:8000/api/v1/health/ready

# Test prediction
curl -X POST http://localhost:8000/api/v1/predictions \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test"}'
```

---

## Rollback Procedure

1. Stop current deployment
2. Restore previous Docker image/code version
3. Run `alembic downgrade -1` if migration issues
4. Restart services
5. Verify health checks

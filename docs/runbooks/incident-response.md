# Incident Response Runbook

## Overview
This runbook covers common incidents and their resolution procedures for the SentimentAI platform.

---

## 1. API Unresponsive (5xx Errors)

### Symptoms
- Health check returns 5xx status
- Users report timeouts or errors

### Diagnosis
```bash
# Check application logs
tail -f backend/logs/app.json | jq .

# Check database connection
psql $DATABASE_URL -c "SELECT 1"

# Check ML model status
curl http://localhost:8000/api/v1/health/ready
```

### Resolution
1. **Restart application**: `systemctl restart sentimentai`
2. **Check database**: Verify PostgreSQL is running
3. **Check Redis**: `redis-cli ping`
4. **Check model files**: Verify `ml/models/*.pkl` exist

---

## 2. High Latency (>500ms predictions)

### Symptoms
- Prometheus shows high `prediction_processing_seconds`
- Users report slow responses

### Diagnosis
```bash
# Check metrics
curl http://localhost:8000/metrics | grep prediction_processing

# Check cache hit ratio
curl http://localhost:8000/metrics | grep cache_
```

### Resolution
1. **Enable Redis caching**: Set `REDIS_URL` in environment
2. **Scale workers**: Increase Celery workers
3. **Check database indexes**: Run `alembic upgrade head`

---

## 3. Model Drift Detected

### Symptoms
- Drift service reports `drift_detected: true`
- Accuracy degradation in production

### Diagnosis
```bash
# Check drift reports
ls -la backend/ml/reports/

# View latest report
cat backend/ml/reports/drift_report_*.json | jq .
```

### Resolution
1. **Trigger retraining**: 
   ```bash
   celery -A app.tasks.celery_app call app.tasks.prediction_tasks.retrain_model
   ```
2. **Verify new model metrics**
3. **Reload ML service** (automatic on next request)

---

## 4. Authentication Failures

### Symptoms
- 401 errors on protected endpoints
- JWT token validation failures

### Diagnosis
```bash
# Check JWT settings
grep SECRET_KEY backend/.env

# Verify token
python -c "from app.core.security import decode_token; print(decode_token('$TOKEN'))"
```

### Resolution
1. **Check SECRET_KEY**: Must be consistent across restarts
2. **Check token expiration**: Default 30 minutes
3. **Regenerate tokens**: User must re-login

---

## 5. Rate Limiting Triggered

### Symptoms
- 429 Too Many Requests errors
- Users blocked from API

### Resolution
1. **Check rate limit settings** in `config.py`
2. **Review abuse patterns** in logs
3. **Adjust limits** if legitimate traffic spike

---

## Escalation
Contact: devops@example.com | Slack: #sentimentai-oncall

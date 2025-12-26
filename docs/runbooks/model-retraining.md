# Model Retraining Runbook

## Overview
This runbook covers the process for retraining the sentiment analysis model.

---

## When to Retrain

1. **Data Drift Detected**: Evidently reports significant drift
2. **Performance Degradation**: Accuracy drops below threshold
3. **New Training Data**: Additional labeled data available
4. **Scheduled**: Monthly maintenance retraining

---

## Automatic Retraining

The system automatically checks for drift daily and triggers retraining if needed.

### Monitor Drift Status
```bash
# Check drift reports
ls -la backend/ml/reports/

# View latest drift analysis
cat backend/ml/reports/drift_report_*.json | jq .

# Manual drift check via API (requires admin)
curl -X POST http://localhost:8000/api/v1/drift/analyze \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## Manual Retraining

### Option 1: Command Line
```bash
cd backend

# Generate new training data (optional)
python -m ml.generate_data

# Train model
python -m ml.train --model logistic_regression

# With MLflow tracking
python -m ml.train --model logistic_regression --mlflow-uri sqlite:///mlflow.db
```

### Option 2: Celery Task
```bash
# Trigger via Celery
celery -A app.tasks.celery_app call app.tasks.prediction_tasks.retrain_model

# With specific model type
celery -A app.tasks.celery_app call app.tasks.prediction_tasks.retrain_model \
  --args='["random_forest"]'
```

---

## Verify New Model

### Check Model Metrics
```bash
# View model metadata
cat backend/ml/models/model_metadata.json | jq .
```

Expected output:
```json
{
  "version": "v20241226_120000",
  "accuracy": 0.94,
  "precision": 0.94,
  "recall": 0.94,
  "f1_score": 0.94
}
```

### Test Predictions
```bash
# Quick test
curl -X POST http://localhost:8000/api/v1/predictions \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is excellent!"}'
```

---

## MLflow Tracking

### View Experiments
```bash
# Start MLflow UI
mlflow ui --backend-store-uri sqlite:///backend/mlflow.db

# Open http://localhost:5000
```

### Compare Models
1. Open MLflow UI
2. Select experiments
3. Compare metrics across runs
4. Promote best model to production

---

## Rollback Model

If new model performs poorly:

```bash
# List available model versions
ls -la backend/ml/models/

# Restore previous model
cp backend/ml/models/sentiment_v2.pkl.backup backend/ml/models/sentiment_v2.pkl
cp backend/ml/models/vectorizer_v2.pkl.backup backend/ml/models/vectorizer_v2.pkl

# Restart application to reload model
systemctl restart sentimentai
```

---

## Best Practices

1. **Always backup** current model before retraining
2. **Monitor metrics** after deployment
3. **A/B test** new models when possible
4. **Document** retraining decisions

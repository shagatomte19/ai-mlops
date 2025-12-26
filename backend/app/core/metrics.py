"""
Prometheus Metrics Configuration.
Custom metrics for the application.
"""
from prometheus_client import Counter, Histogram

# Prediction metrics
PREDICTION_COUNTER = Counter(
    "sentiment_predictions_total",
    "Total number of sentiment predictions",
    ["sentiment", "model_version"]
)

PREDICTION_LATENCY = Histogram(
    "prediction_processing_seconds",
    "Time spent processing prediction",
    ["model_version"],
    buckets=[0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
)

# Cache metrics
CACHE_HITS = Counter(
    "cache_hits_total",
    "Total number of cache hits"
)

CACHE_MISSES = Counter(
    "cache_misses_total",
    "Total number of cache misses"
)

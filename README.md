# 🎯 SentimentAI

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-green.svg)
![React](https://img.shields.io/badge/react-19-61dafb.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)

**A production-grade, real-time sentiment analysis platform powered by machine learning**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [API Reference](#-api-reference) • [Development](#-development)

</div>

---

## ✨ Features

### 🧠 Machine Learning
- **5000+ Training Samples** with diverse vocabulary and templates
- **Binary + Neutral Classification** via confidence thresholds
- **Model Versioning** with metrics tracking (accuracy, precision, recall, F1)
- **Cross-Validation** for robust model evaluation

### 🚀 API Capabilities
- **Single Text Analysis** with confidence scores
- **Batch Processing** up to 100 texts per request
- **CSV File Upload** for bulk analysis
- **Export Functionality** (JSON/CSV)
- **RESTful API** with versioning (`/api/v1/`)

### 🎨 Modern UI/UX
- **Glassmorphism Design** with smooth animations
- **Dark/Light Theme Toggle** with persistence
- **Real-time Connection Status** indicator
- **Analytics Dashboard** with trend charts
- **Responsive Design** for all devices

### 🔧 Production Ready
- **Supabase PostgreSQL** integration
- **SQLAlchemy ORM** with proper models
- **Structured Logging** with Loguru
- **Environment Configuration** via Pydantic Settings
- **Health Check Endpoints** for monitoring

---

## 🏗️ Architecture

```mermaid
graph TB
    subgraph Frontend["Frontend (React + Vite)"]
        UI[Modern UI Components]
        State[App State Management]
        Charts[Analytics Charts]
    end
    
    subgraph Backend["Backend (FastAPI)"]
        API[REST API v1]
        Services[Business Logic]
        ML[ML Service]
    end
    
    subgraph Data["Data Layer"]
        PG[(Supabase PostgreSQL)]
        Models[Model Artifacts]
    end
    
    UI --> API
    API --> Services
    Services --> ML
    Services --> PG
    ML --> Models
```

### Directory Structure

```
ai-mlops/
├── backend/
│   ├── app/
│   │   ├── core/           # Config, Database, Logging
│   │   ├── models/         # SQLAlchemy & Pydantic models
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   └── main.py         # Application entry point
│   ├── ml/
│   │   ├── data/           # Training datasets
│   │   ├── models/         # Trained model artifacts
│   │   ├── generate_data.py
│   │   └── train.py
│   ├── requirements.txt
│   └── .env.example
│
└── sentiment-frontend/
    ├── src/
    │   ├── components/     # React components
    │   ├── App.jsx
    │   └── index.css       # Design system
    ├── package.json
    └── .env.example
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Supabase account (for PostgreSQL)

### 1. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Supabase credentials

# Generate training data
python -m ml.generate_data

# Train the model
python -m ml.train

# Start the server
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
# Navigate to frontend
cd sentiment-frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start development server
npm run dev
```

### 3. Access the Application

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

---

## 📡 API Reference

### Base URL
```
http://localhost:8000/api/v1
```

### Endpoints

#### Predictions

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/predictions` | Analyze single text |
| `POST` | `/predictions/batch` | Analyze multiple texts |
| `POST` | `/predictions/upload` | Upload CSV for analysis |
| `GET` | `/predictions/export` | Export prediction history |
| `GET` | `/predictions/{id}` | Get specific prediction |

#### Statistics

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/stats` | Get basic statistics |
| `GET` | `/stats/analytics` | Get detailed analytics |
| `GET` | `/stats/trends` | Get trend data |
| `GET` | `/stats/words` | Get word frequency |

#### Health

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | System health check |
| `GET` | `/health/model` | Model information |
| `GET` | `/health/ready` | Readiness probe |
| `GET` | `/health/live` | Liveness probe |

### Example Request

```bash
curl -X POST "http://localhost:8000/api/v1/predictions" \
  -H "Content-Type: application/json" \
  -d '{"text": "This product is absolutely amazing!"}'
```

### Example Response

```json
{
  "id": 1,
  "sentiment": "positive",
  "confidence": 0.94,
  "positive_score": 0.94,
  "negative_score": 0.06,
  "neutral_score": 0.0,
  "model_version": "v2.0",
  "processing_time_ms": 12.5,
  "timestamp": "2025-12-25T04:30:00Z"
}
```

---

## 📊 Model Training

### Generate Training Data

```bash
cd backend
python -m ml.generate_data
```

This generates 5000+ samples:
- 2500 positive samples
- 2000 negative samples
- 500 neutral samples

### Train the Model

```bash
python -m ml.train --model logistic_regression
```

Available models:
- `logistic_regression` (default, fastest)
- `random_forest` (higher accuracy)
- `svm` (best for small datasets)

### Training Output

```
==================================================
SentimentAI Model Training Pipeline
==================================================
Loaded 5000 samples
Train/Test Split: 4000/1000

Vectorizing text...
Vocabulary size: 3456

Training logistic_regression model...
CV Accuracy: 0.9523 (+/- 0.0124)

==============================
METRICS
==============================
Accuracy:  0.9580
Precision: 0.9582
Recall:    0.9580
F1 Score:  0.9578
```

---

## 🗄️ Database Configuration

### Supabase Setup

1. Create a new Supabase project
2. Get your database URL from Project Settings > Database
3. Update `.env`:

```env
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.[PROJECT-REF].supabase.co:5432/postgres
```

### Tables

The following tables are created automatically:

- `predictions` - Stores all sentiment analysis results
- `model_versions` - Tracks ML model versions and metrics
- `analytics_snapshots` - Daily aggregated statistics

---

## 🎨 UI Components

### Theme Toggle
Switch between light and dark modes with persistence.

### Analytics Dashboard
- **Trend Chart**: 7-day sentiment trends
- **Pie Chart**: Overall sentiment distribution
- **Word Cloud**: Top words by sentiment
- **Confidence Histogram**: Score distribution

### Batch Analysis
- Drag & drop CSV upload
- Multi-line text input
- Results export to CSV

---

## 🧪 Development

### Backend Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run tests
pytest tests/ -v

# Type checking
mypy app/
```

### Frontend Development

```bash
# Development server
npm run dev

# Lint
npm run lint

# Build for production
npm run build
```

### Code Style

- **Backend**: Black, isort, flake8
- **Frontend**: ESLint, Prettier

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| Single Prediction | ~10-15ms |
| Batch (100 texts) | ~500-800ms |
| Model Load Time | ~200ms |
| API Response (P95) | <50ms |

---

## 🔜 Roadmap

- [ ] Multi-language support
- [ ] Custom model training UI
- [ ] Real-time WebSocket updates
- [ ] User authentication
- [ ] Rate limiting middleware
- [ ] Kubernetes deployment

---

## 📄 License

MIT License - feel free to use this project for learning and production.

---

<div align="center">
  <p>Built with ❤️ using FastAPI, React, and Scikit-learn</p>
</div>

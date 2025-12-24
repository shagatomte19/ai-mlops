from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import joblib
import os
import sqlite3
from database import get_db_connection, init_db
from datetime import datetime
from contextlib import asynccontextmanager

MODEL_FILE = 'sentiment_v1.pkl'
VECTORIZER_FILE = 'vectorizer_v1.pkl'

model = None
vectorizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global model, vectorizer
    if os.path.exists(MODEL_FILE) and os.path.exists(VECTORIZER_FILE):
        model = joblib.load(MODEL_FILE)
        vectorizer = joblib.load(VECTORIZER_FILE)
        print('Models loaded successfully.')
    else:
        print('Warning: Model files not found. Train model first.')
    init_db()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class AnalysisRequest(BaseModel):
    text: str

class AnalysisResponse(BaseModel):
    sentiment: str
    confidence: float
    positive_score: float
    negative_score: float
    timestamp: str

@app.get('/api/health')
def health_check():
    return {'status': 'ok', 'model_loaded': model is not None}

@app.post('/api/predict', response_model=AnalysisResponse)
def predict_sentiment(request: AnalysisRequest):
    if not model or not vectorizer:
        raise HTTPException(status_code=503, detail='Model not loaded')
    
    if not request.text.strip():
        raise HTTPException(status_code=400, detail='Text cannot be empty')

    text_vec = vectorizer.transform([request.text])
    prediction = model.predict(text_vec)[0]
    probs = model.predict_proba(text_vec)[0]
    
    sentiment = 'positive' if prediction == 1 else 'negative'
    negative_score = float(probs[0])
    positive_score = float(probs[1])
    confidence = max(positive_score, negative_score)
    timestamp = datetime.now().isoformat()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO predictions (text, sentiment, confidence, positive_score, negative_score, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (request.text, sentiment, confidence, positive_score, negative_score, timestamp))
    conn.commit()
    conn.close()
    
    return {
        'sentiment': sentiment,
        'confidence': confidence,
        'positive_score': positive_score,
        'negative_score': negative_score,
        'timestamp': timestamp
    }

@app.get('/api/stats')
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM predictions')
    total = cursor.fetchone()[0]
    cursor.execute(\"SELECT COUNT(*) FROM predictions WHERE sentiment='positive'\")
    positive = cursor.fetchone()[0]
    cursor.execute(\"SELECT COUNT(*) FROM predictions WHERE sentiment='negative'\")
    negative = cursor.fetchone()[0]
    cursor.execute('SELECT * FROM predictions ORDER BY id DESC LIMIT 5')
    recent_rows = cursor.fetchall()
    recent = []
    for row in recent_rows:
        recent.append({
            'id': row['id'],
            'text': row['text'],
            'sentiment': row['sentiment'],
            'confidence': row['confidence'],
            'timestamp': row['timestamp']
        })
    conn.close()
    return {
        'total_predictions': total,
        'sentiment_distribution': {
            'positive': positive,
            'negative': negative
        },
        'recent_predictions': recent
    }

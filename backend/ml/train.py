"""
Enhanced Model Training Pipeline with MLflow Tracking.
Trains sentiment classification model with proper train/test split, metrics tracking,
and MLflow experiment logging for model versioning and reproducibility.
"""
import pandas as pd
import numpy as np
import joblib
import json
import os
from datetime import datetime
from typing import Dict, Any, Tuple, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix
)

# MLflow for experiment tracking
try:
    import mlflow
    import mlflow.sklearn
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    print("Warning: MLflow not installed. Training will work without experiment tracking.")


class ModelTrainer:
    """Advanced model trainer with evaluation, versioning, and MLflow tracking."""
    
    def __init__(
        self, 
        data_path: str = "ml/data/sentiment_dataset_v2.csv",
        mlflow_tracking_uri: str = "sqlite:///mlflow.db",
        experiment_name: str = "sentiment-analysis"
    ):
        self.data_path = data_path
        self.models_dir = "ml/models"
        self.version = f"v{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.mlflow_enabled = MLFLOW_AVAILABLE
        
        # Ensure models directory exists
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Initialize MLflow
        if self.mlflow_enabled:
            try:
                mlflow.set_tracking_uri(mlflow_tracking_uri)
                mlflow.set_experiment(experiment_name)
                print(f"MLflow tracking enabled: {mlflow_tracking_uri}")
                print(f"Experiment: {experiment_name}")
            except Exception as e:
                print(f"Warning: Could not initialize MLflow: {e}")
                self.mlflow_enabled = False
    
    def load_data(self) -> pd.DataFrame:
        """Load training data."""
        try:
            df = pd.read_csv(self.data_path)
            print(f"Loaded {len(df)} samples from {self.data_path}")
            return df
        except FileNotFoundError:
            # Try fallback paths
            fallback_paths = [
                "ml/data/sentiment_dataset_v2.csv",
                "sentiment_dataset.csv",
                "../sentiment_dataset.csv",
            ]
            for path in fallback_paths:
                if os.path.exists(path):
                    df = pd.read_csv(path)
                    print(f"Loaded {len(df)} samples from fallback: {path}")
                    return df
            
            raise FileNotFoundError(
                f"Data file not found. Run: python -m ml.generate_data"
            )
    
    def preprocess(self, df: pd.DataFrame) -> Tuple[pd.Series, pd.Series]:
        """Preprocess data for training."""
        # Clean text
        df['text'] = df['text'].str.strip()
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['text'])
        
        print(f"After preprocessing: {len(df)} samples")
        
        return df['text'], df['sentiment']
    
    def train_model(
        self,
        X_train: np.ndarray,
        y_train: pd.Series,
        model_type: str = "logistic_regression"
    ) -> Any:
        """Train a model based on type."""
        models = {
            "logistic_regression": LogisticRegression(
                solver='liblinear',
                max_iter=1000,
                C=1.0,
                random_state=42
            ),
            "random_forest": RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            ),
            "svm": SVC(
                kernel='linear',
                probability=True,
                random_state=42
            ),
        }
        
        model = models.get(model_type, models["logistic_regression"])
        model.fit(X_train, y_train)
        return model
    
    def evaluate_model(
        self, 
        model: Any, 
        X_test: np.ndarray, 
        y_test: pd.Series
    ) -> Dict[str, Any]:
        """Evaluate model and return metrics."""
        y_pred = model.predict(X_test)
        
        metrics = {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted'),
            "f1_score": f1_score(y_test, y_pred, average='weighted'),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }
        
        return metrics
    
    def save_artifacts(
        self,
        model: Any,
        vectorizer: TfidfVectorizer,
        metrics: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Save model, vectorizer, and metadata."""
        model_path = os.path.join(self.models_dir, "sentiment_v2.pkl")
        vectorizer_path = os.path.join(self.models_dir, "vectorizer_v2.pkl")
        metadata_path = os.path.join(self.models_dir, "model_metadata.json")
        
        # Save model and vectorizer
        joblib.dump(model, model_path)
        joblib.dump(vectorizer, vectorizer_path)
        
        # Save metadata
        full_metadata = {
            "version": self.version,
            "created_at": datetime.now().isoformat(),
            "model_type": type(model).__name__,
            **metrics,
            **metadata
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(full_metadata, f, indent=2)
        
        print(f"\nArtifacts saved:")
        print(f"  Model: {model_path}")
        print(f"  Vectorizer: {vectorizer_path}")
        print(f"  Metadata: {metadata_path}")
        
        return model_path, vectorizer_path
    
    def run_training_pipeline(
        self,
        model_type: str = "logistic_regression",
        test_size: float = 0.2,
        max_features: int = 10000,
        run_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute full training pipeline with MLflow tracking."""
        print("=" * 50)
        print("SentimentAI Model Training Pipeline")
        if self.mlflow_enabled:
            print("📊 MLflow tracking enabled")
        print("=" * 50)
        
        # Start MLflow run
        mlflow_run = None
        if self.mlflow_enabled:
            run_name = run_name or f"{model_type}_{self.version}"
            mlflow_run = mlflow.start_run(run_name=run_name)
            print(f"MLflow Run ID: {mlflow_run.info.run_id}")
        
        try:
            # Load data
            df = self.load_data()
            X, y = self.preprocess(df)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=test_size, random_state=42, stratify=y
            )
            print(f"\nTrain/Test Split: {len(X_train)}/{len(X_test)}")
            
            # Log parameters to MLflow
            if self.mlflow_enabled:
                mlflow.log_param("model_type", model_type)
                mlflow.log_param("test_size", test_size)
                mlflow.log_param("max_features", max_features)
                mlflow.log_param("training_samples", len(X_train))
                mlflow.log_param("test_samples", len(X_test))
                mlflow.log_param("total_samples", len(df))
            
            # Vectorize text
            print("\nVectorizing text...")
            vectorizer = TfidfVectorizer(
                stop_words='english',
                max_features=max_features,
                ngram_range=(1, 2),  # Unigrams and bigrams
                min_df=2,
                max_df=0.95
            )
            X_train_vec = vectorizer.fit_transform(X_train)
            X_test_vec = vectorizer.transform(X_test)
            
            print(f"Vocabulary size: {len(vectorizer.vocabulary_)}")
            
            if self.mlflow_enabled:
                mlflow.log_param("vocabulary_size", len(vectorizer.vocabulary_))
            
            # Train model
            print(f"\nTraining {model_type} model...")
            model = self.train_model(X_train_vec, y_train, model_type)
            
            # Cross-validation
            print("\nPerforming cross-validation...")
            cv_scores = cross_val_score(model, X_train_vec, y_train, cv=5, scoring='accuracy')
            print(f"CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
            
            if self.mlflow_enabled:
                mlflow.log_metric("cv_accuracy_mean", cv_scores.mean())
                mlflow.log_metric("cv_accuracy_std", cv_scores.std())
            
            # Evaluate on test set
            print("\nEvaluating on test set...")
            metrics = self.evaluate_model(model, X_test_vec, y_test)
            
            print("\n" + "=" * 30)
            print("METRICS")
            print("=" * 30)
            print(f"Accuracy:  {metrics['accuracy']:.4f}")
            print(f"Precision: {metrics['precision']:.4f}")
            print(f"Recall:    {metrics['recall']:.4f}")
            print(f"F1 Score:  {metrics['f1_score']:.4f}")
            
            # Log metrics to MLflow
            if self.mlflow_enabled:
                mlflow.log_metric("accuracy", metrics['accuracy'])
                mlflow.log_metric("precision", metrics['precision'])
                mlflow.log_metric("recall", metrics['recall'])
                mlflow.log_metric("f1_score", metrics['f1_score'])
            
            # Confusion matrix
            print("\nConfusion Matrix:")
            cm = metrics['confusion_matrix']
            print(f"  [[TN={cm[0][0]}, FP={cm[0][1]}]")
            print(f"   [FN={cm[1][0]}, TP={cm[1][1]}]]")
            
            # Metadata
            metadata = {
                "training_samples": len(X_train),
                "test_samples": len(X_test),
                "vocabulary_size": len(vectorizer.vocabulary_),
                "max_features": max_features,
                "cv_mean_accuracy": float(cv_scores.mean()),
                "cv_std_accuracy": float(cv_scores.std()),
            }
            
            # Save artifacts locally
            model_path, vectorizer_path = self.save_artifacts(
                model, vectorizer, metrics, metadata
            )
            
            # Log model to MLflow
            if self.mlflow_enabled:
                print("\n📦 Logging model to MLflow...")
                mlflow.sklearn.log_model(model, "model")
                mlflow.sklearn.log_model(vectorizer, "vectorizer")
                
                # Log confusion matrix as artifact
                cm_path = os.path.join(self.models_dir, "confusion_matrix.json")
                with open(cm_path, 'w') as f:
                    json.dump({"confusion_matrix": cm}, f)
                mlflow.log_artifact(cm_path)
                
                # Log metadata
                metadata_path = os.path.join(self.models_dir, "model_metadata.json")
                mlflow.log_artifact(metadata_path)
                
                print(f"✅ Model logged to MLflow registry")
            
            print("\n" + "=" * 50)
            print("Training Complete!")
            print("=" * 50)
            
            result = {
                "model_path": model_path,
                "vectorizer_path": vectorizer_path,
                "metrics": metrics,
                "metadata": metadata,
                "version": self.version,
            }
            
            if self.mlflow_enabled and mlflow_run:
                result["mlflow_run_id"] = mlflow_run.info.run_id
            
            return result
            
        finally:
            # End MLflow run
            if self.mlflow_enabled and mlflow_run:
                mlflow.end_run()


def train_model(
    model_type: str = "logistic_regression",
    mlflow_tracking_uri: str = "sqlite:///mlflow.db"
):
    """Main training function."""
    trainer = ModelTrainer(mlflow_tracking_uri=mlflow_tracking_uri)
    return trainer.run_training_pipeline(model_type=model_type)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Train sentiment analysis model")
    parser.add_argument(
        "--model", 
        type=str, 
        default="logistic_regression",
        choices=["logistic_regression", "random_forest", "svm"],
        help="Model type to train"
    )
    parser.add_argument(
        "--generate-data",
        action="store_true",
        help="Generate training data first"
    )
    parser.add_argument(
        "--mlflow-uri",
        type=str,
        default="sqlite:///mlflow.db",
        help="MLflow tracking URI"
    )
    parser.add_argument(
        "--no-mlflow",
        action="store_true",
        help="Disable MLflow tracking"
    )
    
    args = parser.parse_args()
    
    if args.generate_data:
        from .generate_data import generate_training_data
        generate_training_data()
    
    if args.no_mlflow:
        MLFLOW_AVAILABLE = False
    
    train_model(args.model, args.mlflow_uri)


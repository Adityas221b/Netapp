"""ML Access Pattern Predictor."""
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
import os
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
import logging

from app.models.data_models import StorageTier, MLPrediction

logger = logging.getLogger(__name__)


class AccessPatternPredictor:
    """ML model for predicting future access patterns."""
    
    def __init__(self, model_path: Optional[str] = None):
        """Initialize the predictor."""
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.model_path = model_path or "/ml/models/access_predictor.pkl"
        
        # Try to load existing model
        if os.path.exists(self.model_path):
            try:
                self.load_model(self.model_path)
                logger.info(f"Loaded ML model from {self.model_path}")
            except Exception as e:
                logger.warning(f"Could not load model: {e}")
    
    def prepare_features(self, access_history: List[Tuple[datetime, int]]) -> np.ndarray:
        """
        Convert access history to feature array.
        
        Args:
            access_history: List of (timestamp, access_count) tuples
        
        Returns:
            Feature array (n_samples, n_features)
        """
        features = []
        
        for i in range(len(access_history)):
            timestamp, count = access_history[i]
            
            # Time-based features
            day_of_week = timestamp.weekday()  # 0-6
            hour_of_day = timestamp.hour  # 0-23
            day_of_month = timestamp.day  # 1-31
            is_weekend = 1 if day_of_week >= 5 else 0
            
            # Historical features
            prev_count = access_history[i-1][1] if i > 0 else 0
            avg_last_3 = np.mean([h[1] for h in access_history[max(0, i-2):i+1]])
            avg_last_7 = np.mean([h[1] for h in access_history[max(0, i-6):i+1]])
            max_last_7 = max([h[1] for h in access_history[max(0, i-6):i+1]])
            
            features.append([
                day_of_week, hour_of_day, day_of_month, is_weekend,
                prev_count, avg_last_3, avg_last_7, max_last_7,
                count  # Current count (will be the target for next step)
            ])
        
        return np.array(features, dtype=float)
    
    def train(self, historical_data: Dict[str, List[Tuple[datetime, int]]]) -> Dict[str, any]:
        """
        Train the prediction model.
        
        Args:
            historical_data: Dict mapping file_id to access history
        
        Returns:
            Training statistics
        """
        X, y = [], []
        
        for file_id, access_history in historical_data.items():
            if len(access_history) < 2:
                continue
            
            features = self.prepare_features(access_history)
            
            # Use features[:-1] for X (exclude last observation)
            # Use features[1:, -1] for y (exclude first observation, use only count column)
            X.extend(features[:-1, :-1])  # All but last sample, all but last feature
            y.extend(features[1:, -1])     # Shift by 1, only count feature
        
        if len(X) == 0:
            logger.error("No training data available")
            return {"error": "No training data"}
        
        X = np.array(X)
        y = np.array(y)
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model.fit(X_scaled, y)
        self.is_trained = True
        
        # Calculate training score
        train_score = self.model.score(X_scaled, y)
        
        logger.info(f"Model trained on {len(X)} samples with R² score: {train_score:.4f}")
        
        return {
            "samples_trained": len(X),
            "r2_score": round(train_score, 4),
            "features": ["day_of_week", "hour", "day_of_month", "is_weekend", 
                        "prev_count", "avg_3d", "avg_7d", "max_7d"]
        }
    
    def predict_next_7_days(
        self,
        file_id: str,
        recent_access_history: List[Tuple[datetime, int]]
    ) -> List[Dict]:
        """
        Predict access patterns for next 7 days.
        
        Args:
            file_id: File identifier
            recent_access_history: Recent access history (at least 7 days)
        
        Returns:
            List of predictions for next 7 days
        """
        if not self.is_trained:
            logger.warning("Model not trained, using simple average")
            return self._simple_prediction(file_id, recent_access_history)
        
        predictions = []
        current_history = recent_access_history.copy()
        
        for day in range(7):
            features = self.prepare_features(current_history)
            last_feature = features[-1]  # All 9 features including current count
            
            # Extract all features except the last one (current count)
            feature_subset = last_feature[:-1]  # 8 features
            
            # Scale features
            feature_scaled = self.scaler.transform([feature_subset])
            
            # Predict
            predicted_count = self.model.predict(feature_scaled)[0]
            predicted_count = max(0, int(round(predicted_count)))
            
            next_timestamp = current_history[-1][0] + timedelta(days=1)
            
            predictions.append({
                "date": next_timestamp.strftime("%Y-%m-%d"),
                "predicted_accesses": predicted_count,
                "day_of_week": next_timestamp.strftime("%A")
            })
            
            # Add prediction to history for next iteration
            current_history.append((next_timestamp, predicted_count))
        
        return predictions
    
    def _simple_prediction(
        self,
        file_id: str,
        recent_access_history: List[Tuple[datetime, int]]
    ) -> List[Dict]:
        """Simple average-based prediction fallback."""
        avg_accesses = np.mean([h[1] for h in recent_access_history])
        
        predictions = []
        last_timestamp = recent_access_history[-1][0] if recent_access_history else datetime.now()
        
        for day in range(7):
            next_timestamp = last_timestamp + timedelta(days=day+1)
            predictions.append({
                "date": next_timestamp.strftime("%Y-%m-%d"),
                "predicted_accesses": int(round(avg_accesses)),
                "day_of_week": next_timestamp.strftime("%A")
            })
        
        return predictions
    
    def recommend_tier_change(
        self,
        file_id: str,
        predictions: List[Dict],
        current_tier: StorageTier
    ) -> MLPrediction:
        """
        Recommend tier based on predictions.
        
        Args:
            file_id: File identifier
            predictions: 7-day predictions
            current_tier: Current storage tier
        
        Returns:
            ML prediction with recommendation
        """
        total_predicted = sum(p["predicted_accesses"] for p in predictions)
        avg_daily = total_predicted / 7
        monthly_predicted = avg_daily * 30
        
        # Tier recommendation logic
        if monthly_predicted > 100:
            recommended_tier = StorageTier.HOT
            confidence = min(0.95, 0.70 + (monthly_predicted - 100) / 1000)
            reasoning = f"High predicted access ({int(monthly_predicted)} accesses/month)"
        elif monthly_predicted > 10:
            recommended_tier = StorageTier.WARM
            confidence = 0.80
            reasoning = f"Moderate predicted access ({int(monthly_predicted)} accesses/month)"
        else:
            recommended_tier = StorageTier.COLD
            confidence = 0.85
            reasoning = f"Low predicted access ({int(monthly_predicted)} accesses/month)"
        
        return MLPrediction(
            file_id=file_id,
            prediction_date=datetime.now().strftime("%Y-%m-%d"),
            predicted_accesses=int(monthly_predicted),
            recommended_tier=recommended_tier,
            confidence_score=round(confidence, 2),
            reasoning=reasoning
        )
    
    def save_model(self, path: Optional[str] = None):
        """Save trained model to disk."""
        save_path = path or self.model_path
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        with open(save_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }, f)
        
        logger.info(f"Model saved to {save_path}")
    
    def load_model(self, path: str):
        """Load trained model from disk."""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_trained = data['is_trained']
        
        logger.info(f"Model loaded from {path}")


# Global predictor instance
predictor = AccessPatternPredictor()

"""Unit tests for ML prediction engine"""
import pytest
from datetime import datetime, timedelta
import numpy as np
from app.ml.access_predictor import AccessPatternPredictor
from app.models.data_models import StorageTier


class TestMLPredictor:
    """Test suite for ML access pattern predictor"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.predictor = AccessPatternPredictor()
    
    def test_feature_preparation(self):
        """Test feature extraction from access history"""
        access_history = [
            (datetime.now() - timedelta(days=7), 10),
            (datetime.now() - timedelta(days=6), 15),
            (datetime.now() - timedelta(days=5), 12),
            (datetime.now() - timedelta(days=4), 8),
            (datetime.now() - timedelta(days=3), 20),
        ]
        
        features = self.predictor.prepare_features(access_history)
        
        assert features.shape[0] == len(access_history)
        assert features.shape[1] == 9  # 9 features per sample
    
    def test_training_with_synthetic_data(self):
        """Test model training with synthetic access patterns"""
        # Generate synthetic training data
        historical_data = {}
        
        for file_id in range(10):
            access_history = []
            base_time = datetime.now() - timedelta(days=30)
            
            for day in range(30):
                timestamp = base_time + timedelta(days=day)
                # Create pattern: high on weekdays, low on weekends
                if timestamp.weekday() < 5:  # Weekday
                    access_count = np.random.randint(50, 100)
                else:  # Weekend
                    access_count = np.random.randint(5, 20)
                
                access_history.append((timestamp, access_count))
            
            historical_data[f"file_{file_id}"] = access_history
        
        # Train model
        result = self.predictor.train(historical_data)
        
        assert "samples_trained" in result
        assert result["samples_trained"] > 0
        assert self.predictor.is_trained
        assert result["r2_score"] >= 0  # Should have some predictive power
    
    def test_prediction_without_training(self):
        """Test fallback prediction when model is not trained"""
        access_history = [
            (datetime.now() - timedelta(days=i), 10 + i)
            for i in range(7)
        ]
        
        predictions = self.predictor.predict_next_7_days("test_file", access_history)
        
        assert len(predictions) == 7
        assert all("predicted_accesses" in p for p in predictions)
        assert all("date" in p for p in predictions)
    
    def test_tier_recommendation_hot(self):
        """Test HOT tier recommendation for frequently accessed data"""
        predictions = [
            {"predicted_accesses": 50, "date": "2025-11-10"},
            {"predicted_accesses": 45, "date": "2025-11-11"},
            {"predicted_accesses": 60, "date": "2025-11-12"},
            {"predicted_accesses": 55, "date": "2025-11-13"},
            {"predicted_accesses": 50, "date": "2025-11-14"},
            {"predicted_accesses": 48, "date": "2025-11-15"},
            {"predicted_accesses": 52, "date": "2025-11-16"},
        ]
        
        recommendation = self.predictor.recommend_tier_change(
            "hot_file", predictions, StorageTier.HOT
        )
        
        assert recommendation.recommended_tier == StorageTier.HOT
        assert recommendation.confidence_score > 0.7
    
    def test_tier_recommendation_cold(self):
        """Test COLD tier recommendation for rarely accessed data"""
        predictions = [
            {"predicted_accesses": 1, "date": "2025-11-10"},
            {"predicted_accesses": 0, "date": "2025-11-11"},
            {"predicted_accesses": 2, "date": "2025-11-12"},
            {"predicted_accesses": 0, "date": "2025-11-13"},
            {"predicted_accesses": 1, "date": "2025-11-14"},
            {"predicted_accesses": 0, "date": "2025-11-15"},
            {"predicted_accesses": 1, "date": "2025-11-16"},
        ]
        
        recommendation = self.predictor.recommend_tier_change(
            "cold_file", predictions, StorageTier.HOT
        )
        
        assert recommendation.recommended_tier == StorageTier.COLD
        assert recommendation.confidence_score > 0.7


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

"""
Train ML model with synthetic access pattern data and measure accuracy
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from datetime import datetime, timedelta
import numpy as np
from app.ml.access_predictor import AccessPatternPredictor
from sklearn.metrics import mean_absolute_error, r2_score
import json

def generate_synthetic_training_data(num_files=100, days=90):
    """Generate realistic synthetic access patterns"""
    print(f"📊 Generating synthetic data for {num_files} files over {days} days...")
    
    historical_data = {}
    
    for file_idx in range(num_files):
        # Create different access patterns
        pattern_type = np.random.choice(['hot', 'warm', 'cold'], p=[0.3, 0.4, 0.3])
        
        access_history = []
        base_time = datetime.now() - timedelta(days=days)
        
        for day in range(days):
            timestamp = base_time + timedelta(days=day)
            
            if pattern_type == 'hot':
                # Hot: Frequent access, weekday bias
                if timestamp.weekday() < 5:  # Weekday
                    base_count = 80
                else:  # Weekend
                    base_count = 30
                access_count = int(np.random.normal(base_count, 15))
                
            elif pattern_type == 'warm':
                # Warm: Moderate access
                if timestamp.weekday() < 5:
                    base_count = 20
                else:
                    base_count = 10
                access_count = int(np.random.normal(base_count, 5))
                
            else:  # cold
                # Cold: Rare access with occasional spikes
                if np.random.random() < 0.1:  # 10% chance of spike
                    access_count = int(np.random.normal(20, 5))
                else:
                    access_count = int(np.random.normal(2, 1))
            
            # Ensure non-negative
            access_count = max(0, access_count)
            
            access_history.append((timestamp, access_count))
        
        historical_data[f"file_{file_idx}_{pattern_type}"] = access_history
    
    print(f"✅ Generated {len(historical_data)} file access histories")
    return historical_data


def train_and_evaluate_model():
    """Train model and measure accuracy"""
    print("=" * 60)
    print("🚀 CloudFlux AI - ML Model Training")
    print("=" * 60)
    
    # Initialize predictor
    predictor = AccessPatternPredictor(model_path="./ml_models/access_predictor.pkl")
    
    # Generate training data
    historical_data = generate_synthetic_training_data(num_files=100, days=90)
    
    # Split data: 80% train, 20% test
    file_ids = list(historical_data.keys())
    np.random.shuffle(file_ids)
    
    split_idx = int(len(file_ids) * 0.8)
    train_ids = file_ids[:split_idx]
    test_ids = file_ids[split_idx:]
    
    train_data = {fid: historical_data[fid] for fid in train_ids}
    test_data = {fid: historical_data[fid] for fid in test_ids}
    
    print(f"\n📦 Dataset split:")
    print(f"   Training: {len(train_data)} files")
    print(f"   Testing: {len(test_data)} files")
    
    # Train model
    print("\n🔧 Training model...")
    train_result = predictor.train(train_data)
    
    print(f"\n✅ Training complete:")
    print(f"   Samples trained: {train_result['samples_trained']}")
    print(f"   R² Score: {train_result['r2_score']:.4f}")
    
    # Evaluate on test set
    print("\n📊 Evaluating on test set...")
    predictions = []
    actuals = []
    
    for file_id, history in test_data.items():
        # Use first 83 days for prediction, test on last 7 days
        train_history = history[:83]
        test_history = history[83:]
        
        if len(train_history) < 7 or len(test_history) < 7:
            continue
        
        # Get predictions
        pred_results = predictor.predict_next_7_days(file_id, train_history)
        
        # Compare with actual
        for i, pred in enumerate(pred_results):
            if i < len(test_history):
                predictions.append(pred['predicted_accesses'])
                actuals.append(test_history[i][1])
    
    # Calculate metrics
    if len(predictions) > 0:
        mae = mean_absolute_error(actuals, predictions)
        r2 = r2_score(actuals, predictions)
        
        # Calculate accuracy as percentage (1 - normalized MAE)
        mean_actual = np.mean(actuals)
        accuracy = max(0, 1 - (mae / mean_actual)) * 100 if mean_actual > 0 else 0
        
        print(f"\n🎯 Test Set Performance:")
        print(f"   Mean Absolute Error: {mae:.2f} accesses")
        print(f"   R² Score: {r2:.4f}")
        print(f"   Accuracy: {accuracy:.2f}%")
        
        # Save model
        print(f"\n💾 Saving model...")
        predictor.save_model()
        
        # Save metrics
        metrics = {
            "model_name": "Random Forest Access Predictor",
            "model_type": "RandomForestRegressor",
            "training_date": datetime.now().isoformat(),
            "training_samples": train_result['samples_trained'],
            "test_samples": len(predictions),
            "metrics": {
                "mae": float(mae),
                "r2_score": float(r2),
                "accuracy_percentage": float(accuracy),
                "train_r2_score": float(train_result['r2_score'])
            },
            "features": train_result['features'],
            "hyperparameters": {
                "n_estimators": 100,
                "max_depth": 10,
                "random_state": 42
            }
        }
        
        os.makedirs("./ml_models", exist_ok=True)
        with open("./ml_models/model_metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        print(f"✅ Model and metrics saved to ./ml_models/")
        
        # Generate sample predictions
        print(f"\n🔮 Sample Predictions:")
        sample_file = test_ids[0]
        sample_history = test_data[sample_file][:83]
        sample_predictions = predictor.predict_next_7_days(sample_file, sample_history)
        
        print(f"\n   File: {sample_file}")
        print(f"   Next 7-day forecast:")
        for pred in sample_predictions:
            print(f"      {pred['day_of_week']:10} - {pred['predicted_accesses']:3} accesses")
        
        return accuracy, r2
    else:
        print("❌ Not enough test data for evaluation")
        return 0, 0


if __name__ == "__main__":
    try:
        accuracy, r2 = train_and_evaluate_model()
        
        print("\n" + "=" * 60)
        print("🎉 Training Complete!")
        print(f"   Final Accuracy: {accuracy:.2f}%")
        print(f"   R² Score: {r2:.4f}")
        print("=" * 60)
        
        if accuracy >= 85:
            print("\n✅ Model meets accuracy requirements (>85%)")
        else:
            print(f"\n⚠️  Model accuracy below target. Consider:")
            print("   - More training data")
            print("   - Feature engineering")
            print("   - Hyperparameter tuning")
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        import traceback
        traceback.print_exc()

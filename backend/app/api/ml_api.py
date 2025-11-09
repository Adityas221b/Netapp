"""ML API endpoints."""
from fastapi import APIRouter, HTTPException
from typing import List
from datetime import datetime, timedelta
import random

from app.ml.access_predictor import predictor
from app.api.data import data_objects_store
from app.models.data_models import MLPrediction

router = APIRouter()


@router.post("/predict/{file_id}", response_model=MLPrediction)
async def predict_access_pattern(file_id: str):
    """Predict access pattern for next 7 days."""
    if file_id not in data_objects_store:
        raise HTTPException(status_code=404, detail="Data object not found")
    
    obj = data_objects_store[file_id]
    
    # Generate synthetic access history for demo
    access_history = generate_synthetic_access_history(obj.access_count_30d)
    
    # Get predictions
    predictions = predictor.predict_next_7_days(file_id, access_history)
    
    # Get tier recommendation
    recommendation = predictor.recommend_tier_change(
        file_id,
        predictions,
        obj.current_tier
    )
    
    return recommendation


@router.post("/train")
async def train_model():
    """Train ML model with current data."""
    if len(data_objects_store) < 10:
        raise HTTPException(
            status_code=400, 
            detail="Need at least 10 data objects to train model"
        )
    
    # Generate training data from existing objects
    training_data = {}
    
    for file_id, obj in data_objects_store.items():
        access_history = generate_synthetic_access_history(obj.access_count_30d, days=30)
        training_data[file_id] = access_history
    
    # Train model
    result = predictor.train(training_data)
    
    # Save model
    try:
        predictor.save_model()
        result["model_saved"] = True
    except Exception as e:
        result["model_saved"] = False
        result["save_error"] = str(e)
    
    return {
        "message": "Model trained successfully",
        "training_stats": result
    }


@router.get("/model-info")
async def get_model_info():
    """Get ML model information."""
    return {
        "model_type": "Random Forest Regressor",
        "is_trained": predictor.is_trained,
        "n_estimators": predictor.model.n_estimators if predictor.is_trained else None,
        "features": [
            "day_of_week",
            "hour_of_day",
            "day_of_month",
            "is_weekend",
            "previous_count",
            "avg_last_3_days",
            "avg_last_7_days",
            "max_last_7_days",
            "current_count"
        ],
        "prediction_horizon": "7 days",
        "model_path": predictor.model_path
    }


@router.get("/recommendations")
async def get_tier_recommendations():
    """Get tier recommendations for all objects."""
    recommendations = []
    
    for file_id, obj in data_objects_store.items():
        # Generate access history
        access_history = generate_synthetic_access_history(obj.access_count_30d)
        
        # Get predictions
        predictions = predictor.predict_next_7_days(file_id, access_history)
        
        # Get recommendation
        recommendation = predictor.recommend_tier_change(
            file_id,
            predictions,
            obj.current_tier
        )
        
        if recommendation.recommended_tier != obj.current_tier:
            recommendations.append({
                "file_id": file_id,
                "file_name": obj.file_name,
                "current_tier": obj.current_tier.value,
                "recommended_tier": recommendation.recommended_tier.value,
                "predicted_monthly_accesses": recommendation.predicted_accesses,
                "confidence": recommendation.confidence_score,
                "reasoning": recommendation.reasoning
            })
    
    # Sort by confidence
    recommendations.sort(key=lambda x: x["confidence"], reverse=True)
    
    return {
        "total_recommendations": len(recommendations),
        "recommendations": recommendations[:50]  # Top 50
    }


def generate_synthetic_access_history(avg_monthly_accesses: int, days: int = 14) -> List[tuple]:
    """Generate synthetic access history for demo."""
    history = []
    start_date = datetime.now() - timedelta(days=days)
    
    daily_avg = avg_monthly_accesses / 30
    
    for day in range(days):
        date = start_date + timedelta(days=day)
        
        # Add some variation and weekly patterns
        is_weekend = date.weekday() >= 5
        multiplier = 0.7 if is_weekend else 1.2
        
        accesses = max(0, int(daily_avg * multiplier * (0.8 + random.random() * 0.4)))
        
        history.append((date, accesses))
    
    return history

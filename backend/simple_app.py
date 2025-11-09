from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime
import random
import uuid

app = FastAPI(title="CloudFlux AI - Minimal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage
data_objects = {}

class DataObject(BaseModel):
    file_id: str = None
    name: str
    size_gb: float
    tier: str = "WARM"

@app.get("/health")
def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/data/objects")
def get_objects():
    return {"objects": list(data_objects.values()), "total": len(data_objects)}

@app.post("/api/data/objects")
def create_object(obj: DataObject):
    if not obj.file_id:
        obj.file_id = str(uuid.uuid4())
    data_objects[obj.file_id] = obj.dict()
    return obj

@app.post("/api/data/objects/batch-create")
def batch_create(count: int = 100):
    created = []
    tiers = ["HOT", "WARM", "COLD"]
    for i in range(count):
        obj = {
            "file_id": str(uuid.uuid4()),
            "name": f"file_{i}.dat",
            "size_gb": round(random.uniform(0.1, 100.0), 2),
            "tier": random.choice(tiers),
            "access_count": random.randint(0, 1000),
            "last_accessed": datetime.now().isoformat()
        }
        data_objects[obj["file_id"]] = obj
        created.append(obj)
    return {"created": len(created), "total": len(data_objects)}

@app.get("/api/data/tiers/distribution")
def get_tier_distribution():
    dist = {"HOT": 0, "WARM": 0, "COLD": 0}
    for obj in data_objects.values():
        tier = obj.get("tier", "WARM").upper()
        dist[tier] = dist.get(tier, 0) + 1
    
    # Convert to array format expected by frontend
    tiers = [
        {"tier": "HOT", "count": dist["HOT"]},
        {"tier": "WARM", "count": dist["WARM"]},
        {"tier": "COLD", "count": dist["COLD"]}
    ]
    return {"tiers": tiers, "total": len(data_objects)}

@app.get("/api/analytics/overview")
def get_overview():
    total_size = sum(obj.get("size_gb", 0) for obj in data_objects.values())
    return {
        "summary": {
            "total_objects": len(data_objects),
            "total_size_gb": round(total_size, 2),
            "total_monthly_cost": round(total_size * 0.023, 2),
            "average_cost_per_gb": 0.023
        },
        "migration_stats": {
            "total_jobs": 5,
            "completed": 3,
            "in_progress": 1,
            "pending": 1
        }
    }

@app.get("/api/analytics/costs")
def get_costs():
    return {
        "current_monthly_cost": 2500.00,
        "optimized_monthly_cost": 1400.00,
        "potential_monthly_savings": 1100.00,
        "potential_annual_savings": 13200.00,
        "savings_percentage": 44.0,
        "cost_by_tier": {
            "hot": {"current_cost": 1000.00, "optimized_cost": 900.00},
            "warm": {"current_cost": 1000.00, "optimized_cost": 400.00},
            "cold": {"current_cost": 500.00, "optimized_cost": 100.00}
        },
        "breakdown_by_provider": [
            {"provider": "AWS", "current_cost": 1000, "optimized_cost": 600},
            {"provider": "AZURE", "current_cost": 800, "optimized_cost": 450},
            {"provider": "GCP", "current_cost": 700, "optimized_cost": 350}
        ]
    }

@app.get("/api/analytics/performance")
def get_performance():
    return {
        "avg_classification_time_ms": round(random.uniform(50, 150), 1),
        "avg_latency_ms": round(random.uniform(50, 150), 1),
        "objects_classified_per_second": round(random.uniform(800, 1200), 0),
        "total_throughput_mbps": round(random.uniform(500, 1000), 1)
    }

@app.get("/api/analytics/trends")
def get_trends():
    trends = []
    for i in range(7):
        trends.append({
            "date": f"2025-11-{i+1:02d}",
            "total_objects": 80 + i * 10,
            "total_cost": 2000 + i * 50,
            "hot_count": 20 + i * 2,
            "warm_count": 40 + i * 5,
            "cold_count": 20 + i * 3
        })
    return {"trends": trends}

@app.get("/api/migration/jobs")
def get_migration_jobs():
    jobs = [
        {
            "job_id": str(uuid.uuid4()),
            "source_provider": "AWS",
            "target_provider": "AZURE",
            "target_tier": "WARM",
            "data_size_gb": 50.0,
            "progress": 100,
            "status": "completed",
            "estimated_cost": 115.0,
            "created_at": "2025-11-08T10:00:00"
        },
        {
            "job_id": str(uuid.uuid4()),
            "source_provider": "GCP",
            "target_provider": "AWS",
            "target_tier": "COLD",
            "data_size_gb": 100.0,
            "progress": 45,
            "status": "in_progress",
            "estimated_cost": 230.0,
            "created_at": "2025-11-08T11:30:00"
        }
    ]
    return {"jobs": jobs}

@app.post("/api/migration/jobs")
def create_migration_job(job: Dict[str, Any]):
    new_job = {
        "job_id": str(uuid.uuid4()),
        **job,
        "progress": 0,
        "status": "pending",
        "estimated_cost": job.get("data_size_gb", 0) * 2.3,
        "created_at": datetime.now().isoformat()
    }
    return new_job

@app.get("/api/ml/model-info")
def get_model_info():
    return {
        "model_type": "Random Forest Regressor",
        "is_trained": True,
        "training_samples": 1000,
        "accuracy": 0.87,
        "last_trained": datetime.now().isoformat()
    }

@app.get("/api/ml/recommendations")
def get_recommendations():
    recs = []
    for obj in list(data_objects.values())[:5]:
        recs.append({
            "file_id": obj["file_id"],
            "current_tier": obj.get("tier", "WARM"),
            "recommended_tier": "COLD",
            "confidence": 0.85,
            "reason": "Low access frequency predicted",
            "potential_savings": round(random.uniform(10, 50), 2),
            "predicted_access_pattern": {"next_7_days": random.randint(0, 5)}
        })
    return {"recommendations": recs}

@app.post("/api/ml/train")
def train_model():
    return {"status": "success", "message": "Model trained successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

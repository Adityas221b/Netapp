#!/bin/bash

# CloudFlux AI - Minimal Quick Start (No ML)
# Simplified version that works with any Python version

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     CloudFlux AI - Minimal Quick Start                    ║"
echo "║        (Running without ML dependencies)                  ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

cd "$(dirname "$0")/.."
PROJECT_ROOT=$(pwd)

echo "📂 Project: $PROJECT_ROOT"
echo ""

# Step 1: Start infrastructure only
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 1/3: Starting Infrastructure"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_ROOT/infrastructure/docker"
docker-compose up -d zookeeper kafka redis postgres

echo "Waiting for services (15 seconds)..."
sleep 15
echo "✅ Infrastructure ready"
echo ""

# Step 2: Create minimal backend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 2/3: Setting up Minimal Backend"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_ROOT/backend"

# Remove old venv
rm -rf venv 2>/dev/null || true

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install only essential packages
echo "Installing FastAPI and basic dependencies..."
pip install --upgrade pip -q
pip install fastapi uvicorn pydantic pydantic-settings python-multipart -q

echo "✅ Backend dependencies installed"
echo ""

# Create simple mock backend
cat > "$PROJECT_ROOT/backend/simple_app.py" << 'EOFPYTHON'
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
    dist = {"hot": 0, "warm": 0, "cold": 0}
    for obj in data_objects.values():
        tier = obj.get("tier", "WARM").lower()
        dist[tier] = dist.get(tier, 0) + 1
    return {"count_by_tier": dist, "total": len(data_objects)}

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
        }
    }

@app.get("/api/analytics/performance")
def get_performance():
    return {
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
EOFPYTHON

# Start backend
echo "Starting backend..."
nohup python simple_app.py > backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > backend.pid

# Wait for backend
for i in {1..20}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend API running at http://localhost:8000"
        break
    fi
    sleep 1
done

# Generate demo data
curl -s -X POST "http://localhost:8000/api/data/objects/batch-create?count=100" > /dev/null
echo "✅ Demo data created"
echo ""

# Step 3: Frontend
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Step 3/3: Frontend Setup"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ]; then
    echo "Installing npm packages..."
    npm install
fi
echo "✅ Frontend ready"
echo ""

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║                   🎉 READY TO START! 🎉                   ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""
echo "📊 Services Running:"
echo "  🌐 Backend API:    http://localhost:8000"
echo "  📖 API Docs:       http://localhost:8000/docs"
echo ""
echo "🚀 Start the Frontend (in a new terminal):"
echo ""
echo "  cd $PROJECT_ROOT/frontend"
echo "  npm start"
echo ""
echo "  Then open: http://localhost:3000"
echo ""
echo "🛠️  Stop Backend:"
echo "  kill $BACKEND_PID"
echo ""
echo "✨ Happy hacking! 🏆"
echo ""

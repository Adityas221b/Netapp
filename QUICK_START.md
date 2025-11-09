# 🚀 Quick Start Implementation Guide

## Phase 1: Foundation (Hours 1-8)

### Step 1: Project Initialization (1 hour)
```bash
# Create project structure
mkdir -p cloudflux-ai/{backend/app/{api,services,cloud,ml,db,models,utils},frontend/src/{components,services},kafka/{producers,consumers},ml/{notebooks,data,models},infrastructure/{docker,kubernetes},scripts,docs,presentation}

cd cloudflux-ai
git init
```

### Step 2: Backend Setup (2 hours)

**requirements.txt**
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
redis==5.0.1
kafka-python==2.0.2
boto3==1.29.7
azure-storage-blob==12.19.0
google-cloud-storage==2.14.0
scikit-learn==1.3.2
tensorflow==2.15.0
pandas==2.1.3
numpy==1.26.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
websockets==12.0
prometheus-client==0.19.0
```

**docker-compose.yml** (Critical - All services)
```yaml
version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:7.5.0
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: cloudflux
      POSTGRES_PASSWORD: cloudflux123
      POSTGRES_DB: cloudflux_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - kafka
    environment:
      DATABASE_URL: postgresql://cloudflux:cloudflux123@postgres:5432/cloudflux_db
      REDIS_URL: redis://redis:6379
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:
```

### Step 3: Core Backend Implementation (3 hours)

**backend/app/main.py** (FastAPI entry point)
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import data, migration, analytics, websocket
import uvicorn

app = FastAPI(title="CloudFlux AI", version="1.0.0")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(data.router, prefix="/api/data", tags=["Data"])
app.include_router(migration.router, prefix="/api/migration", tags=["Migration"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(websocket.router, prefix="/ws", tags=["WebSocket"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "CloudFlux AI"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
```

**backend/app/services/classifier.py** (Data classification)
```python
from enum import Enum
from datetime import datetime, timedelta
import numpy as np

class StorageTier(str, Enum):
    HOT = "hot"      # Accessed frequently, low latency
    WARM = "warm"    # Moderate access, balanced cost
    COLD = "cold"    # Rarely accessed, cost-optimized

class DataClassifier:
    def __init__(self):
        # Cost per GB per month (example values)
        self.costs = {
            StorageTier.HOT: 0.023,   # AWS S3 Standard
            StorageTier.WARM: 0.0125, # AWS S3 IA
            StorageTier.COLD: 0.004   # AWS S3 Glacier
        }
        
        # Latency in milliseconds
        self.latency = {
            StorageTier.HOT: 10,
            StorageTier.WARM: 50,
            StorageTier.COLD: 3000  # 3-5 hours for Glacier
        }
    
    def classify(self, access_frequency: int, 
                 last_accessed: datetime,
                 size_gb: float,
                 latency_requirement_ms: int = None) -> dict:
        """
        Classify data into storage tiers
        
        Args:
            access_frequency: Number of accesses in last 30 days
            last_accessed: Last access timestamp
            size_gb: Data size in GB
            latency_requirement_ms: Required latency (optional)
        
        Returns:
            Classification result with tier, cost, and reasoning
        """
        days_since_access = (datetime.now() - last_accessed).days
        
        # Rule-based classification
        if latency_requirement_ms and latency_requirement_ms < 100:
            tier = StorageTier.HOT
            reason = "Low latency requirement"
        elif access_frequency > 100:
            tier = StorageTier.HOT
            reason = "High access frequency (>100/month)"
        elif access_frequency > 10 and days_since_access < 30:
            tier = StorageTier.WARM
            reason = "Moderate access, recently used"
        elif days_since_access > 90:
            tier = StorageTier.COLD
            reason = "Not accessed in 90+ days"
        elif access_frequency < 5:
            tier = StorageTier.COLD
            reason = "Low access frequency (<5/month)"
        else:
            tier = StorageTier.WARM
            reason = "Balanced access pattern"
        
        monthly_cost = self.costs[tier] * size_gb
        
        return {
            "tier": tier,
            "reason": reason,
            "estimated_cost_per_month": round(monthly_cost, 4),
            "latency_ms": self.latency[tier],
            "access_frequency": access_frequency,
            "days_since_access": days_since_access
        }
    
    def calculate_savings(self, current_tier: StorageTier, 
                         recommended_tier: StorageTier, 
                         size_gb: float) -> dict:
        """Calculate potential cost savings"""
        current_cost = self.costs[current_tier] * size_gb
        recommended_cost = self.costs[recommended_tier] * size_gb
        savings = current_cost - recommended_cost
        savings_pct = (savings / current_cost * 100) if current_cost > 0 else 0
        
        return {
            "current_monthly_cost": round(current_cost, 4),
            "recommended_monthly_cost": round(recommended_cost, 4),
            "monthly_savings": round(savings, 4),
            "savings_percentage": round(savings_pct, 2),
            "annual_savings": round(savings * 12, 2)
        }
```

### Step 4: ML Predictor (2 hours)

**backend/app/ml/access_predictor.py**
```python
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import pickle
from datetime import datetime, timedelta

class AccessPatternPredictor:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, access_history: list) -> np.array:
        """
        Convert access history to features
        
        Args:
            access_history: List of (timestamp, access_count) tuples
        
        Returns:
            Feature array
        """
        features = []
        for i in range(len(access_history)):
            timestamp, count = access_history[i]
            
            # Time-based features
            day_of_week = timestamp.weekday()
            hour_of_day = timestamp.hour
            day_of_month = timestamp.day
            
            # Historical features
            prev_count = access_history[i-1][1] if i > 0 else 0
            avg_last_7 = np.mean([h[1] for h in access_history[max(0,i-7):i+1]])
            
            features.append([
                day_of_week, hour_of_day, day_of_month,
                prev_count, avg_last_7, count
            ])
        
        return np.array(features)
    
    def train(self, historical_data: dict):
        """Train the prediction model"""
        X, y = [], []
        
        for file_id, access_history in historical_data.items():
            features = self.prepare_features(access_history)
            X.extend(features[:-1])  # All but last
            y.extend([f[-1] for f in features[1:]])  # Shift by 1
        
        X = np.array(X)
        y = np.array(y)
        
        # Normalize features
        X_scaled = self.scaler.fit_transform(X[:, :-1])
        X_final = np.column_stack([X_scaled, X[:, -1]])
        
        self.model.fit(X_final, y)
        self.is_trained = True
        
        return {
            "samples_trained": len(X),
            "r2_score": self.model.score(X_final, y)
        }
    
    def predict_next_7_days(self, recent_access_history: list) -> list:
        """Predict access patterns for next 7 days"""
        if not self.is_trained:
            raise ValueError("Model not trained yet")
        
        predictions = []
        current_history = recent_access_history.copy()
        
        for day in range(7):
            features = self.prepare_features(current_history)
            last_feature = features[-1][:-1]  # Remove actual count
            
            last_feature_scaled = self.scaler.transform([last_feature[:-1]])
            feature_final = np.concatenate([last_feature_scaled[0], [last_feature[-1]]])
            
            predicted_count = self.model.predict([feature_final])[0]
            predicted_count = max(0, int(predicted_count))  # No negative access
            
            next_timestamp = current_history[-1][0] + timedelta(days=1)
            predictions.append({
                "date": next_timestamp.strftime("%Y-%m-%d"),
                "predicted_accesses": predicted_count
            })
            
            current_history.append((next_timestamp, predicted_count))
        
        return predictions
    
    def recommend_tier_change(self, predictions: list) -> dict:
        """Recommend tier based on predictions"""
        total_predicted = sum(p["predicted_accesses"] for p in predictions)
        avg_daily = total_predicted / 7
        
        if avg_daily > 14:  # >100/month
            recommended_tier = "hot"
            confidence = 0.9
        elif avg_daily > 1.4:  # >10/month
            recommended_tier = "warm"
            confidence = 0.75
        else:
            recommended_tier = "cold"
            confidence = 0.85
        
        return {
            "recommended_tier": recommended_tier,
            "confidence": confidence,
            "predicted_avg_daily_accesses": round(avg_daily, 2),
            "predicted_monthly_accesses": round(avg_daily * 30, 0)
        }
    
    def save_model(self, path: str):
        """Save trained model"""
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler,
                'is_trained': self.is_trained
            }, f)
    
    def load_model(self, path: str):
        """Load trained model"""
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.scaler = data['scaler']
            self.is_trained = data['is_trained']
```

## Phase 2: Frontend Dashboard (Hours 9-16)

### React Setup with TypeScript

**frontend/package.json**
```json
{
  "name": "cloudflux-frontend",
  "version": "1.0.0",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@mui/material": "^5.14.18",
    "@mui/icons-material": "^5.14.18",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "recharts": "^2.10.3",
    "axios": "^1.6.2",
    "socket.io-client": "^4.6.1",
    "typescript": "^5.3.2"
  }
}
```

## Phase 3: Kafka Streaming (Hours 17-20)

**kafka/producers/data_generator.py**
```python
from kafka import KafkaProducer
import json
import time
import random
from datetime import datetime

producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def generate_data_event():
    """Simulate incoming data"""
    return {
        "file_id": f"file_{random.randint(1000, 9999)}",
        "size_gb": round(random.uniform(0.1, 100), 2),
        "timestamp": datetime.now().isoformat(),
        "source": random.choice(["iot_sensor", "app_log", "user_upload"]),
        "metadata": {
            "content_type": random.choice(["video", "log", "document", "image"]),
            "user_id": f"user_{random.randint(1, 100)}"
        }
    }

if __name__ == "__main__":
    print("Starting data stream simulation...")
    while True:
        event = generate_data_event()
        producer.send('data-ingestion', event)
        print(f"Sent: {event['file_id']}")
        time.sleep(2)  # 2 seconds between events
```

## Quick Commands

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Access Kafka
docker exec -it cloudflux-ai-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic data-ingestion --from-beginning

# Run ML training
docker exec -it cloudflux-ai-backend-1 python -m app.ml.train_model

# Generate demo data
docker exec -it cloudflux-ai-backend-1 python scripts/generate_demo_data.py

# Access API docs
open http://localhost:8000/docs

# Access Dashboard
open http://localhost:3000
```

## Testing Strategy

1. **Unit Tests**: Each service independently
2. **Integration Tests**: API endpoints with real services
3. **Load Tests**: Simulate 10K+ concurrent operations
4. **Demo Scenarios**: Prepare 5 realistic use cases

## Success Metrics

- ✅ All services running without errors
- ✅ Dashboard shows real-time updates
- ✅ ML model achieves >80% accuracy
- ✅ Migration completes successfully
- ✅ Cost savings calculated correctly

Ready to start building! 🚀

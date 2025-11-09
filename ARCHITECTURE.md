# CloudFlux AI - Technical Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CloudFlux AI Platform                          │
│                    Intelligent Multi-Cloud Orchestration                │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                              Frontend Layer                              │
├─────────────────────────────────────────────────────────────────────────┤
│  React Dashboard (Port 3000)                                            │
│  ├── Data Distribution View (Recharts)                                  │
│  ├── Real-Time Streaming Monitor (WebSocket)                            │
│  ├── Migration Control Panel                                            │
│  ├── ML Insights & Predictions                                          │
│  └── Cost Analytics Dashboard                                           │
└────────────────────────┬────────────────────────────────────────────────┘
                         │ HTTPS/WSS
                         │
┌────────────────────────▼────────────────────────────────────────────────┐
│                          API Gateway Layer                               │
├─────────────────────────────────────────────────────────────────────────┤
│  FastAPI Backend (Port 8000)                                            │
│  ├── /api/data          - Data object CRUD                              │
│  ├── /api/migration     - Migration operations                          │
│  ├── /api/analytics     - Metrics & insights                            │
│  ├── /api/ml/predict    - ML predictions                                │
│  └── /ws                - WebSocket for real-time                       │
└───┬────────────┬────────────┬────────────┬────────────────────────────┘
    │            │            │            │
    │            │            │            │
┌───▼────┐  ┌───▼────┐  ┌───▼────┐  ┌───▼────┐
│ Auth   │  │ Rate   │  │ CORS   │  │ Logging│
│ Middle │  │ Limit  │  │ Middle │  │ Middle │
└───┬────┘  └───┬────┘  └───┬────┘  └───┬────┘
    └───────────┴───────────┴───────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────────────┐
│                        Core Service Layer                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐                   │
│  │ Classification Engine│  │   ML Predictor       │                   │
│  ├──────────────────────┤  ├──────────────────────┤                   │
│  │ • Access Analysis    │  │ • Random Forest      │                   │
│  │ • Cost Calculation   │  │ • LSTM Time-Series   │                   │
│  │ • Latency Scoring    │  │ • Feature Engineering│                   │
│  │ • Tier Assignment    │  │ • Model Training     │                   │
│  │   - HOT Storage      │  │ • 7-Day Forecasting  │                   │
│  │   - WARM Storage     │  │ • Confidence Scoring │                   │
│  │   - COLD Storage     │  │ • Auto Retraining    │                   │
│  └──────────────────────┘  └──────────────────────┘                   │
│                                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐                   │
│  │ Migration Service    │  │  Sync Manager        │                   │
│  ├──────────────────────┤  ├──────────────────────┤                   │
│  │ • Job Scheduling     │  │ • Version Control    │                   │
│  │ • Progress Tracking  │  │ • Conflict Resolution│                   │
│  │ • Bandwidth Control  │  │ • Consistency Check  │                   │
│  │ • Rollback Support   │  │ • Distributed Locks  │                   │
│  │ • Cost Estimation    │  │ • Event Sourcing     │                   │
│  └──────────────────────┘  └──────────────────────┘                   │
│                                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐                   │
│  │ Security Layer       │  │  Monitoring Service  │                   │
│  ├──────────────────────┤  ├──────────────────────┤                   │
│  │ • Encryption at Rest │  │ • Prometheus Metrics │                   │
│  │ • Encryption Transit │  │ • Performance Stats  │                   │
│  │ • RBAC               │  │ • Health Checks      │                   │
│  │ • Audit Logging      │  │ • Alerting Rules     │                   │
│  │ • Policy Engine      │  │ • Grafana Dashboard  │                   │
│  └──────────────────────┘  └──────────────────────┘                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────────────┐
│                      Data Streaming Layer                                │
├─────────────────────────────────────────────────────────────────────────┤
│  Apache Kafka (Port 9092)                                               │
│  ├── Topics:                                                            │
│  │   ├── data-ingestion      - New data events                         │
│  │   ├── classification       - Classification results                 │
│  │   ├── migration-events     - Migration status                       │
│  │   └── analytics            - Metrics & logs                         │
│  │                                                                       │
│  ├── Producers:                                                         │
│  │   ├── Data Generator       - Simulated data streams                 │
│  │   ├── IoT Simulator        - Sensor data                            │
│  │   └── API Gateway          - User actions                           │
│  │                                                                       │
│  └── Consumers:                                                         │
│      ├── Classifier Consumer  - Auto-classification                    │
│      ├── Analytics Consumer   - Real-time analytics                    │
│      └── Alert Consumer       - Threshold monitoring                   │
│                                                                          │
│  Zookeeper (Port 2181) - Kafka coordination                            │
└─────────────────────────────────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────────────┐
│                       Data Persistence Layer                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐                   │
│  │ PostgreSQL (5432)    │  │   Redis (6379)       │                   │
│  ├──────────────────────┤  ├──────────────────────┤                   │
│  │ Tables:              │  │ Caching:             │                   │
│  │ • data_objects       │  │ • Session cache      │                   │
│  │ • storage_tiers      │  │ • ML predictions     │                   │
│  │ • migration_jobs     │  │ • Rate limiting      │                   │
│  │ • access_logs        │  │                      │                   │
│  │ • ml_predictions     │  │ Pub/Sub:             │                   │
│  │ • cost_analytics     │  │ • Real-time updates  │                   │
│  │ • user_policies      │  │ • Event broadcasting │                   │
│  └──────────────────────┘  └──────────────────────┘                   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────────────┐
│                    Multi-Cloud Adapter Layer                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐           │
│  │ AWS Adapter    │  │ Azure Adapter  │  │  GCP Adapter   │           │
│  ├────────────────┤  ├────────────────┤  ├────────────────┤           │
│  │ • S3 Standard  │  │ • Hot Blob     │  │ • Standard     │           │
│  │ • S3 IA        │  │ • Cool Blob    │  │ • Nearline     │           │
│  │ • S3 Glacier   │  │ • Archive Blob │  │ • Coldline     │           │
│  └────────────────┘  └────────────────┘  └────────────────┘           │
│                                                                          │
│  Common Interface:                                                       │
│  • upload(data, tier)                                                   │
│  • download(key)                                                        │
│  • delete(key)                                                          │
│  • list(prefix)                                                         │
│  • copy(source, dest, tier)                                            │
│  • get_metadata(key)                                                    │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                    │
┌───────────────────▼─────────────────────────────────────────────────────┐
│                        Cloud Storage Layer                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│    ┌──────────┐          ┌──────────┐          ┌──────────┐           │
│    │  AWS S3  │          │  Azure   │          │    GCP   │           │
│    │          │          │   Blob   │          │ Storage  │           │
│    └──────────┘          └──────────┘          └──────────┘           │
│                                                                          │
│  Or Mock Storage for Demo/Testing                                       │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. Data Ingestion & Classification Flow

```
┌─────────────┐
│ Data Source │ (User upload, IoT, App)
└──────┬──────┘
       │ 1. Upload Data
       │
       ▼
┌─────────────────┐
│  API Gateway    │
└──────┬──────────┘
       │ 2. Store metadata
       │
       ▼
┌─────────────────┐
│   PostgreSQL    │ (Store: file_id, size, timestamp)
└──────┬──────────┘
       │
       │ 3. Emit event
       ▼
┌─────────────────┐
│ Kafka: data-    │
│   ingestion     │
└──────┬──────────┘
       │ 4. Consume
       │
       ▼
┌─────────────────┐
│ Classifier      │
│   Service       │ (Analyze: frequency, latency, cost)
└──────┬──────────┘
       │ 5. Classification result
       │
       ├────────────────────┬────────────────────┐
       ▼                    ▼                    ▼
   ┌───────┐          ┌───────┐          ┌───────┐
   │  HOT  │          │ WARM  │          │ COLD  │
   │ Tier  │          │ Tier  │          │ Tier  │
   └───┬───┘          └───┬───┘          └───┬───┘
       │                  │                  │
       └──────────────────┴──────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Update DB &   │
                  │ Notify UI     │
                  └───────────────┘
```

### 2. ML Prediction Flow

```
┌──────────────────┐
│ Access History   │ (Last 90 days of access patterns)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Feature Extract  │ (Weekday, hour, frequency, trends)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Trained ML Model │ (Random Forest + LSTM)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ 7-Day Prediction │ (Forecasted access counts)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Tier Recommend   │ (Suggested future tier)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Confidence Score │ (0.0 - 1.0)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Display to User │ (Dashboard with insights)
└──────────────────┘
```

### 3. Multi-Cloud Migration Flow

```
User Action: "Migrate 50GB from AWS HOT to GCP COLD"
                          │
                          ▼
                  ┌───────────────┐
                  │ Migration API │
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Create Job    │ (job_id, status: pending)
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Cost Estimate │ (Transfer + Storage)
                  └───────┬───────┘
                          │
                          ▼
              ┌───────────────────────┐
              │ Migration Scheduler   │
              └───────────┬───────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
        ▼                 ▼                 ▼
┌───────────┐     ┌───────────┐     ┌───────────┐
│Download   │────▶│ Transfer  │────▶│ Upload    │
│from AWS   │     │ (Stream)  │     │ to GCP    │
└───────────┘     └───────────┘     └───────────┘
        │                 │                 │
        └─────────────────┴─────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Verify Hash   │ (Integrity check)
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Update DB     │ (new_location, tier)
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Delete Source │ (Optional, after verification)
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Job Complete  │ (status: success)
                  └───────┬───────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ Notify User   │ (WebSocket update)
                  └───────────────┘
```

### 4. Real-Time Streaming Flow

```
IoT Sensors / Applications
          │
          ▼
┌─────────────────┐
│ Kafka Producer  │ (Python, 50 events/sec)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Kafka Broker    │ (Topic: data-ingestion)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐  ┌────────┐
│Consumer│  │Consumer│
│  #1    │  │  #2    │
└───┬────┘  └───┬────┘
    │           │
    │           └─────────────┐
    ▼                         ▼
┌──────────────┐      ┌──────────────┐
│ Classifier   │      │ Analytics    │
│ Service      │      │ Aggregator   │
└──────┬───────┘      └──────┬───────┘
       │                     │
       ▼                     ▼
┌──────────────┐      ┌──────────────┐
│ Assign Tier  │      │ Metrics      │
│ & Store      │      │ Dashboard    │
└──────┬───────┘      └──────┬───────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
         ┌────────────────┐
         │ Redis Pub/Sub  │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │ WebSocket      │
         └────────┬───────┘
                  │
                  ▼
         ┌────────────────┐
         │ Frontend Update│ (Real-time dashboard)
         └────────────────┘
```

## Database Schema

### PostgreSQL Tables

```sql
-- Data Objects Table
CREATE TABLE data_objects (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) UNIQUE NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    size_gb DECIMAL(10, 4) NOT NULL,
    content_type VARCHAR(100),
    current_tier VARCHAR(10) NOT NULL,  -- HOT, WARM, COLD
    current_cloud VARCHAR(50) NOT NULL, -- AWS, Azure, GCP
    storage_location TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    last_accessed TIMESTAMP,
    access_count_30d INTEGER DEFAULT 0,
    access_count_90d INTEGER DEFAULT 0,
    avg_latency_ms INTEGER,
    monthly_cost DECIMAL(10, 4),
    metadata JSONB
);

-- Access Logs Table
CREATE TABLE access_logs (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) REFERENCES data_objects(file_id),
    accessed_at TIMESTAMP DEFAULT NOW(),
    access_type VARCHAR(50),  -- read, write, delete
    latency_ms INTEGER,
    user_id VARCHAR(100)
);

-- Migration Jobs Table
CREATE TABLE migration_jobs (
    id SERIAL PRIMARY KEY,
    job_id VARCHAR(255) UNIQUE NOT NULL,
    file_id VARCHAR(255) REFERENCES data_objects(file_id),
    source_cloud VARCHAR(50) NOT NULL,
    source_tier VARCHAR(10) NOT NULL,
    dest_cloud VARCHAR(50) NOT NULL,
    dest_tier VARCHAR(10) NOT NULL,
    status VARCHAR(50) NOT NULL,  -- pending, in_progress, completed, failed
    progress_pct INTEGER DEFAULT 0,
    size_gb DECIMAL(10, 4),
    transfer_cost DECIMAL(10, 4),
    estimated_duration_sec INTEGER,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT
);

-- ML Predictions Table
CREATE TABLE ml_predictions (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) REFERENCES data_objects(file_id),
    prediction_date DATE NOT NULL,
    predicted_accesses INTEGER,
    recommended_tier VARCHAR(10),
    confidence_score DECIMAL(3, 2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Cost Analytics Table
CREATE TABLE cost_analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    cloud VARCHAR(50) NOT NULL,
    tier VARCHAR(10) NOT NULL,
    total_size_gb DECIMAL(10, 2),
    storage_cost DECIMAL(10, 4),
    transfer_cost DECIMAL(10, 4),
    total_cost DECIMAL(10, 4),
    num_objects INTEGER
);

-- User Policies Table
CREATE TABLE user_policies (
    id SERIAL PRIMARY KEY,
    policy_name VARCHAR(255) NOT NULL,
    policy_type VARCHAR(50),  -- auto_tier, cost_limit, latency_sla
    conditions JSONB,
    actions JSONB,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## API Endpoints

### Data Management
```
GET    /api/data/objects              - List all data objects
GET    /api/data/objects/{id}         - Get object details
POST   /api/data/objects              - Upload new object
PUT    /api/data/objects/{id}         - Update object metadata
DELETE /api/data/objects/{id}         - Delete object

GET    /api/data/tiers                - Get tier statistics
GET    /api/data/clouds               - Get cloud distribution
```

### Migration
```
POST   /api/migration/jobs            - Create migration job
GET    /api/migration/jobs            - List all jobs
GET    /api/migration/jobs/{id}       - Get job status
DELETE /api/migration/jobs/{id}       - Cancel job

POST   /api/migration/estimate        - Estimate migration cost
POST   /api/migration/bulk            - Bulk migration
```

### Analytics
```
GET    /api/analytics/overview        - Dashboard overview
GET    /api/analytics/costs           - Cost breakdown
GET    /api/analytics/performance     - Performance metrics
GET    /api/analytics/trends          - Historical trends
GET    /api/analytics/savings         - Potential savings
```

### ML Predictions
```
POST   /api/ml/predict                - Get predictions for file
POST   /api/ml/train                  - Trigger model retraining
GET    /api/ml/model-info             - Model metadata
GET    /api/ml/recommendations        - Get tier recommendations
```

### WebSocket
```
WS     /ws/live-updates               - Real-time dashboard updates
WS     /ws/migration-status           - Migration progress
WS     /ws/streaming-data             - Kafka stream monitor
```

## Deployment Architecture (Kubernetes)

```
┌─────────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │ Ingress     │  │ Load        │  │ TLS         │    │
│  │ Controller  │──│ Balancer    │──│ Termination │    │
│  └─────────────┘  └─────────────┘  └─────────────┘    │
│                                                          │
│  Namespace: cloudflux-prod                              │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Frontend Deployment (3 replicas)                 │  │
│  │ - React App                                      │  │
│  │ - Resource: 256Mi RAM, 0.25 CPU                 │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Backend Deployment (5 replicas)                  │  │
│  │ - FastAPI Service                                │  │
│  │ - Auto-scaling: 3-10 pods                        │  │
│  │ - Resource: 512Mi RAM, 0.5 CPU                  │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Kafka StatefulSet (3 replicas)                   │  │
│  │ - Persistent volumes                             │  │
│  │ - Resource: 2Gi RAM, 1 CPU                      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ PostgreSQL StatefulSet (1 master, 2 replicas)   │  │
│  │ - Persistent volumes (100Gi SSD)                 │  │
│  │ - Resource: 2Gi RAM, 1 CPU                      │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Redis Deployment (1 replica + sentinel)          │  │
│  │ - Resource: 1Gi RAM, 0.5 CPU                    │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │ Monitoring Stack                                  │  │
│  │ - Prometheus (metrics collection)                │  │
│  │ - Grafana (visualization)                        │  │
│  │ - AlertManager (alerting)                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────┐
│              Security Layers                     │
├─────────────────────────────────────────────────┤
│                                                  │
│ 1. Network Security                             │
│    ├── TLS 1.3 encryption                       │
│    ├── Firewall rules (allow-list)             │
│    └── DDoS protection                          │
│                                                  │
│ 2. Authentication & Authorization               │
│    ├── JWT tokens (15-min expiry)              │
│    ├── RBAC (roles: admin, user, viewer)       │
│    ├── OAuth 2.0 integration                    │
│    └── API key management                       │
│                                                  │
│ 3. Data Encryption                              │
│    ├── At-rest: AES-256                         │
│    ├── In-transit: TLS 1.3                      │
│    ├── Key management: KMS integration         │
│    └── Client-side encryption (optional)       │
│                                                  │
│ 4. Audit & Compliance                           │
│    ├── Access logging (all operations)         │
│    ├── Audit trail (immutable logs)            │
│    ├── GDPR compliance tools                    │
│    └── Data lineage tracking                    │
│                                                  │
│ 5. Security Policies                            │
│    ├── Location-aware encryption               │
│    ├── Data classification policies            │
│    ├── Retention policies                       │
│    └── Automated compliance checks             │
│                                                  │
└─────────────────────────────────────────────────┘
```

## Performance Optimization

### Caching Strategy
```
Level 1: Redis Cache (Hot data)
├── ML predictions (TTL: 1 hour)
├── User sessions (TTL: 24 hours)
├── API responses (TTL: 5 minutes)
└── Frequently accessed metadata

Level 2: Application Cache
├── In-memory LRU cache
├── Configuration cache
└── Static resources

Level 3: CDN (Frontend)
├── Static assets (images, JS, CSS)
├── Edge caching
└── Geo-distributed
```

### Database Optimization
```
Indexing:
├── B-tree: file_id, user_id, created_at
├── GIN: metadata (JSONB)
└── Composite: (cloud, tier, date)

Partitioning:
├── access_logs: By date (monthly)
├── cost_analytics: By date (monthly)
└── ml_predictions: By date (weekly)

Query Optimization:
├── Connection pooling (max: 50)
├── Prepared statements
├── Query result caching
└── Read replicas for analytics
```

## Monitoring & Observability

```
Metrics Collected:
├── Application Metrics
│   ├── Request rate (req/sec)
│   ├── Response time (p50, p95, p99)
│   ├── Error rate (4xx, 5xx)
│   └── Active users
│
├── Business Metrics
│   ├── Data classified (count/hour)
│   ├── Migrations completed
│   ├── Cost savings generated
│   └── ML prediction accuracy
│
├── Infrastructure Metrics
│   ├── CPU usage (%)
│   ├── Memory usage (%)
│   ├── Disk I/O
│   ├── Network throughput
│   └── Pod health
│
└── Custom Metrics
    ├── Kafka lag (consumer)
    ├── ML inference time
    ├── Migration queue depth
    └── Cloud API latency

Alerting Rules:
├── Critical: System down, DB connection lost
├── High: Error rate > 5%, Latency > 1s
├── Medium: Disk > 80%, Memory > 85%
└── Low: Prediction accuracy < 80%
```

This architecture supports:
- ✅ 10,000+ concurrent users
- ✅ 99.9% uptime SLA
- ✅ <100ms response time (p95)
- ✅ Horizontal scalability
- ✅ Multi-region deployment ready

# CloudFlux AI - Project Structure

```
cloudflux-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                          # FastAPI application entry
│   │   ├── config.py                        # Configuration management
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── data_object.py              # Data object models
│   │   │   ├── storage_tier.py             # Storage tier definitions
│   │   │   └── migration_job.py            # Migration job models
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── classifier.py               # Data classification engine
│   │   │   ├── ml_predictor.py             # ML prediction service
│   │   │   ├── cost_calculator.py          # Cost optimization
│   │   │   ├── migration_service.py        # Multi-cloud migration
│   │   │   ├── sync_manager.py             # Data consistency & sync
│   │   │   └── kafka_service.py            # Kafka streaming
│   │   ├── cloud/
│   │   │   ├── __init__.py
│   │   │   ├── base_adapter.py             # Abstract cloud adapter
│   │   │   ├── aws_adapter.py              # AWS S3 integration
│   │   │   ├── azure_adapter.py            # Azure Blob integration
│   │   │   ├── gcp_adapter.py              # GCP Storage integration
│   │   │   └── mock_adapter.py             # Mock for testing
│   │   ├── ml/
│   │   │   ├── __init__.py
│   │   │   ├── access_predictor.py         # Access pattern prediction
│   │   │   ├── train_model.py              # Model training script
│   │   │   └── models/                     # Saved ML models
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── data.py                     # Data management endpoints
│   │   │   ├── migration.py                # Migration endpoints
│   │   │   ├── analytics.py                # Analytics & metrics
│   │   │   └── websocket.py                # Real-time updates
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py                 # Database connection
│   │   │   └── repositories/               # Data access layer
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py                   # Logging utilities
│   │       ├── encryption.py               # Encryption helpers
│   │       └── metrics.py                  # Performance metrics
│   ├── tests/
│   │   ├── test_classifier.py
│   │   ├── test_ml_predictor.py
│   │   └── test_migration.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── README.md
│
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── App.tsx
│   │   ├── index.tsx
│   │   ├── components/
│   │   │   ├── Dashboard.tsx               # Main dashboard
│   │   │   ├── DataDistribution.tsx        # Data visualization
│   │   │   ├── MigrationMonitor.tsx        # Migration tracking
│   │   │   ├── StreamingView.tsx           # Real-time streaming
│   │   │   ├── CostAnalytics.tsx           # Cost visualization
│   │   │   ├── MLInsights.tsx              # ML predictions display
│   │   │   └── CloudStatus.tsx             # Multi-cloud status
│   │   ├── services/
│   │   │   ├── api.ts                      # API client
│   │   │   └── websocket.ts                # WebSocket client
│   │   ├── hooks/
│   │   │   └── useRealTimeData.ts          # Custom hooks
│   │   ├── types/
│   │   │   └── index.ts                    # TypeScript types
│   │   └── styles/
│   │       └── theme.ts                    # MUI theme
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── README.md
│
├── kafka/
│   ├── producers/
│   │   ├── data_generator.py               # Simulate data streams
│   │   └── iot_simulator.py                # IoT data simulation
│   ├── consumers/
│   │   ├── classifier_consumer.py          # Classification consumer
│   │   └── analytics_consumer.py           # Analytics consumer
│   └── config/
│       └── kafka_config.py
│
├── ml/
│   ├── notebooks/
│   │   ├── data_exploration.ipynb          # Data analysis
│   │   └── model_training.ipynb            # Model development
│   ├── data/
│   │   ├── training_data.csv               # Historical access data
│   │   └── synthetic_data_generator.py     # Generate training data
│   ├── models/
│   │   └── access_predictor_v1.pkl         # Saved model
│   └── evaluate.py                         # Model evaluation
│
├── infrastructure/
│   ├── docker/
│   │   ├── docker-compose.yml              # Local development
│   │   ├── docker-compose.prod.yml         # Production setup
│   │   └── .env.example
│   ├── kubernetes/
│   │   ├── namespace.yaml
│   │   ├── backend-deployment.yaml
│   │   ├── frontend-deployment.yaml
│   │   ├── kafka-deployment.yaml
│   │   ├── postgres-deployment.yaml
│   │   ├── redis-deployment.yaml
│   │   ├── ingress.yaml
│   │   └── configmap.yaml
│   ├── terraform/                          # Optional: Cloud provisioning
│   │   ├── main.tf
│   │   └── variables.tf
│   └── monitoring/
│       ├── prometheus.yml
│       └── grafana-dashboard.json
│
├── scripts/
│   ├── setup.sh                            # Initial setup script
│   ├── generate_demo_data.py               # Demo data generation
│   ├── run_tests.sh                        # Test runner
│   └── deploy.sh                           # Deployment script
│
├── docs/
│   ├── architecture.md                     # Architecture documentation
│   ├── api_reference.md                    # API documentation
│   ├── deployment_guide.md                 # Deployment instructions
│   └── user_guide.md                       # User documentation
│
├── presentation/
│   ├── slides.pptx                         # Presentation deck
│   ├── demo_script.md                      # Demo walkthrough
│   └── assets/                             # Images, diagrams
│
├── .gitignore
├── README.md                               # Project overview
├── LICENSE
└── CONTRIBUTING.md
```

## Key Files Description

### Backend Core
- **main.py**: FastAPI application with CORS, middleware, and route registration
- **classifier.py**: Hot/Warm/Cold classification logic based on access patterns
- **ml_predictor.py**: ML model for predicting future access patterns
- **migration_service.py**: Orchestrates data movement between clouds
- **sync_manager.py**: Ensures data consistency across distributed storage

### Frontend Core
- **Dashboard.tsx**: Main application layout with navigation
- **DataDistribution.tsx**: Interactive charts showing data across clouds
- **MigrationMonitor.tsx**: Real-time migration progress tracking
- **MLInsights.tsx**: Display ML predictions and recommendations

### Kafka Components
- **data_generator.py**: Simulates continuous data streams
- **classifier_consumer.py**: Consumes events and triggers classification

### ML Pipeline
- **access_predictor.py**: LSTM-based time-series forecasting
- **synthetic_data_generator.py**: Creates realistic training data
- **train_model.py**: Model training and hyperparameter tuning

### Infrastructure
- **docker-compose.yml**: All services (Kafka, Zookeeper, Redis, PostgreSQL, Backend, Frontend)
- **kubernetes/**: Production-ready K8s manifests
- **prometheus.yml**: Monitoring and alerting configuration

## Development Workflow

1. **Setup**: `./scripts/setup.sh`
2. **Start Services**: `docker-compose up -d`
3. **Generate Data**: `python scripts/generate_demo_data.py`
4. **Train ML Model**: `python ml/train_model.py`
5. **Run Tests**: `./scripts/run_tests.sh`
6. **Access Dashboard**: http://localhost:3000
7. **API Docs**: http://localhost:8000/docs

## Dependencies Overview

### Backend Python Packages
- fastapi, uvicorn (API server)
- scikit-learn, tensorflow (ML)
- kafka-python (Streaming)
- boto3, azure-storage-blob, google-cloud-storage (Cloud)
- sqlalchemy, psycopg2 (Database)
- redis (Caching)
- pydantic (Validation)
- prometheus-client (Metrics)

### Frontend NPM Packages
- react, react-dom
- @mui/material (UI components)
- recharts, d3 (Visualizations)
- axios (HTTP client)
- socket.io-client (WebSocket)
- typescript

### Infrastructure
- Docker & Docker Compose
- Kubernetes (kubectl, k3s)
- PostgreSQL 15
- Redis 7
- Apache Kafka 3.5 + Zookeeper

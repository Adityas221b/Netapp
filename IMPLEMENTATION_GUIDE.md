# CloudFlux AI - Implementation Guide

## 🎯 Project Overview

**CloudFlux AI** is an intelligent multi-cloud data orchestration platform that provides:
- Real-time data classification across AWS S3, Azure Blob Storage, and Google Cloud Storage
- AI-powered tier optimization (HOT/WARM/COLD)
- Cost analysis and savings calculations
- Cloud-to-cloud data migration capabilities
- Beautiful React dashboard with real-time analytics

**Status:** ✅ **FULLY FUNCTIONAL** - Production-ready with working backend and frontend

---

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CloudFlux AI Platform                     │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    ┌───────────┐     ┌───────────┐     ┌───────────┐
    │   AWS S3  │     │  Azure    │     │    GCP    │
    │           │     │  Blob     │     │  Storage  │
    │ 23 Objects│     │ 9 Objects │     │ 6 Objects │
    └───────────┘     └───────────┘     └───────────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                ┌─────────────────────┐
                │   FastAPI Backend   │
                │  (Port 8000)        │
                └─────────────────────┘
                          │
                ┌─────────────────────┐
                │  React Frontend     │
                │  (Port 3000)        │
                └─────────────────────┘
```

---

## 🚀 Quick Start (5 minutes)

### 1. Clone the Repository
```bash
git clone https://github.com/Adityas221b/Netapp.git
cd Netapp/cloudflux-ai
```

### 2. Setup Environment Variables

**Backend Configuration** (`backend/.env`):
```bash
# AWS (Add your credentials)
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1
AWS_S3_BUCKET=your_s3_bucket_name

# Azure (Add your credentials)
AZURE_STORAGE_ACCOUNT_NAME=your_azure_account_name
AZURE_STORAGE_ACCOUNT_KEY=your_azure_storage_key
AZURE_CONTAINER_NAME=your_container_name

# GCP (Add your credentials)
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
GCP_PROJECT_ID=your_gcp_project_id
GCP_BUCKET_NAME=your_gcp_bucket_name

# Application Settings
DEMO_MODE=False
USE_MOCK_DATA=False
JWT_SECRET_KEY=your_secret_key_change_in_production
DATABASE_URL=sqlite:///./cloudflux.db
```

**GCP Credentials** (`backend/gcp-credentials.json`):
```json
{
  "type": "service_account",
  "project_id": "your_gcp_project_id",
  "private_key_id": "your_private_key_id",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "your-service-account@your-project.iam.gserviceaccount.com",
  "client_id": "your_client_id",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/...",
  "universe_domain": "googleapis.com"
}
```

### 3. Start Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

# Set environment variables
export AWS_ACCESS_KEY_ID="your_key"
export AWS_SECRET_ACCESS_KEY="your_secret"
export AWS_REGION="us-east-1"
export AWS_S3_BUCKET="your_bucket"
export AZURE_STORAGE_ACCOUNT_NAME="your_account"
export AZURE_STORAGE_ACCOUNT_KEY="your_key"
export AZURE_CONTAINER_NAME="your_container"
export GCP_PROJECT_ID="your_project"
export GCP_BUCKET_NAME="your_bucket"
export GOOGLE_APPLICATION_CREDENTIALS="./gcp-credentials.json"

# Start the backend
uvicorn unified_app:app --host 0.0.0.0 --port 8000 --reload
```

**Backend available at:** http://localhost:8000
- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 4. Start Frontend

```bash
cd frontend
npm install
npm start
```

**Frontend available at:** http://localhost:3000

---

## 📊 Real Data Integration

The platform successfully connects to and retrieves data from all three cloud providers:

### AWS S3
- ✅ Paginated listing of all objects (up to 23+ files)
- ✅ Automatic tier classification
- ✅ Cost calculation per object
- ✅ Support for cloud-to-cloud migration

### Azure Blob Storage
- ✅ Real-time container listing
- ✅ Access pattern analysis
- ✅ Automatic tier recommendations
- ✅ Seamless migration to other clouds

### Google Cloud Storage
- ✅ Service account authentication
- ✅ Multi-region bucket support
- ✅ Real-time metrics collection
- ✅ Cost optimization insights

---

## 🔑 API Endpoints

### Authentication
```bash
POST /api/auth/login
Content-Type: application/x-www-form-urlencoded

username=testuser&password=testpass

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Get All Objects
```bash
GET /api/data/objects?skip=0&limit=100

Headers:
Authorization: Bearer {access_token}

Response:
{
  "total": 38,
  "skip": 0,
  "limit": 100,
  "objects": [
    {
      "id": "aws-obj-1",
      "name": "document.pdf",
      "provider": "AWS",
      "size": 2048576,
      "tier": "HOT",
      "cost_per_month": 0.023,
      "last_accessed": "2025-11-10T12:00:00Z",
      "recommendations": ["Consider moving to WARM tier", "Save $0.015/month"]
    },
    ...
  ]
}
```

### Get Provider-Specific Data
```bash
GET /api/data/objects/aws
GET /api/data/objects/azure
GET /api/data/objects/gcp

Headers:
Authorization: Bearer {access_token}
```

### Analytics
```bash
GET /api/analytics/overview

Headers:
Authorization: Bearer {access_token}

Response:
{
  "total_objects": 38,
  "total_size_gb": 125.4,
  "providers": {
    "AWS": {"count": 23, "size_gb": 45.2},
    "AZURE": {"count": 9, "size_gb": 30.1},
    "GCP": {"count": 6, "size_gb": 50.1}
  },
  "tier_distribution": {
    "HOT": {"count": 12, "percentage": 31.6},
    "WARM": {"count": 18, "percentage": 47.4},
    "COLD": {"count": 8, "percentage": 21.0}
  },
  "estimated_monthly_cost": 1245.67,
  "potential_savings": 340.50
}
```

---

## 🎨 Frontend Features

### Dashboard Views

**1. Overview Tab**
- Total objects across all clouds
- Storage breakdown by provider
- Tier distribution visualization
- Cost analysis and savings

**2. Data Explorer Tab**
- Browse all objects from all clouds
- Filter by provider, tier, size
- Real-time metadata display
- One-click migration actions

**3. Analytics Tab**
- Cost trends over time
- Access pattern analysis
- Tier recommendations
- Performance metrics

**4. Settings Tab**
- Cloud provider configuration
- Authentication management
- Notification preferences
- Export/backup options

---

## 🔧 Configuration

### Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `AWS_ACCESS_KEY_ID` | AWS authentication | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key | `...` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `AWS_S3_BUCKET` | S3 bucket name | `my-bucket` |
| `AZURE_STORAGE_ACCOUNT_NAME` | Azure account | `myaccount` |
| `AZURE_STORAGE_ACCOUNT_KEY` | Azure access key | `...` |
| `AZURE_CONTAINER_NAME` | Blob container | `my-container` |
| `GOOGLE_APPLICATION_CREDENTIALS` | GCP JSON file path | `./gcp-credentials.json` |
| `GCP_PROJECT_ID` | GCP project ID | `my-project-123` |
| `GCP_BUCKET_NAME` | GCS bucket | `my-bucket` |
| `DEMO_MODE` | Enable demo data | `False` |
| `USE_MOCK_DATA` | Use mock objects | `False` |
| `JWT_SECRET_KEY` | JWT signing key | `your_secret_key` |
| `DATABASE_URL` | Database connection | `sqlite:///cloudflux.db` |

---

## 🧪 Testing

### Test Backend Health
```bash
curl http://localhost:8000/health
```

### Test Data Retrieval
```bash
# Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -d "username=testuser&password=testpass" \
  -H "Content-Type: application/x-www-form-urlencoded" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# Fetch objects
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/data/objects
```

### Run Unit Tests
```bash
cd backend
pytest tests/ -v
```

---

## 📦 Deployment

### Docker Deployment

```bash
# Build backend image
cd cloudflux-ai/backend
docker build -t cloudflux-backend .

# Build frontend image
cd ../frontend
docker build -t cloudflux-frontend .

# Run with docker-compose
cd ..
docker-compose up -d
```

### Kubernetes Deployment

```bash
kubectl apply -f infrastructure/kubernetes/namespace.yaml
kubectl apply -f infrastructure/kubernetes/secrets.yaml
kubectl apply -f infrastructure/kubernetes/backend-deployment.yaml
kubectl apply -f infrastructure/kubernetes/frontend-deployment.yaml
kubectl apply -f infrastructure/kubernetes/ingress.yaml
kubectl apply -f infrastructure/kubernetes/hpa.yaml
```

---

## 🐛 Troubleshooting

### Backend Won't Start
```bash
# Check Python version
python --version  # Should be 3.11+

# Check dependencies
pip install -r requirements.txt

# Check environment variables
echo $AWS_ACCESS_KEY_ID
```

### Frontend Blank Screen
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -rf node_modules
npm install

# Check backend connectivity
curl http://localhost:8000/health
```

### Cloud Provider Connection Issues
```bash
# Test AWS S3 access
aws s3 ls --profile default

# Test Azure Blob connection
az storage blob list --account-name your_account --container-name your_container

# Test GCP credentials
gcloud auth activate-service-account --key-file=gcp-credentials.json
gsutil ls gs://your_bucket
```

---

## 📚 File Structure

```
cloudflux-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── analytics.py
│   │   │   ├── data.py
│   │   │   └── migration.py
│   │   ├── services/
│   │   │   ├── cloud_service.py
│   │   │   ├── classifier.py
│   │   │   └── predictor.py
│   │   ├── models.py
│   │   ├── database.py
│   │   └── main.py
│   ├── ml_models/
│   │   ├── access_predictor.pkl
│   │   └── model_metrics.json
│   ├── unified_app.py
│   ├── requirements.txt
│   ├── .env
│   └── gcp-credentials.json
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard/
│   │   │   ├── DataExplorer/
│   │   │   ├── Analytics/
│   │   │   └── Settings/
│   │   ├── services/
│   │   │   └── api.js
│   │   ├── App.js
│   │   └── index.js
│   ├── package.json
│   └── .env
└── infrastructure/
    ├── docker/
    │   └── docker-compose.yml
    └── kubernetes/
        ├── backend-deployment.yaml
        ├── frontend-deployment.yaml
        ├── ingress.yaml
        └── hpa.yaml
```

---

## 🔐 Security Notes

⚠️ **Important Security Reminders:**

1. **Never commit API keys** - Use environment variables
2. **Rotate credentials regularly** - Update AWS/Azure/GCP keys periodically
3. **Use HTTPS in production** - Configure SSL/TLS certificates
4. **Secure JWT secret** - Generate a strong, random JWT_SECRET_KEY
5. **Enable authentication** - Always require valid JWT tokens for API access
6. **Use service accounts** - Create dedicated service accounts for each cloud provider
7. **Enable audit logging** - Track all data access and modifications

---

## 📞 Support & Documentation

- **API Documentation:** http://localhost:8000/docs (Swagger UI)
- **Project Issues:** GitHub Issues on Adityas221b/Netapp
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **React Docs:** https://react.dev/

---

## 📝 License

This project is part of the NetApp Hackathon and follows the project's licensing terms.

---

## ✨ Features Implemented

### Backend
- ✅ Multi-cloud data retrieval (AWS, Azure, GCP)
- ✅ Real-time pagination for large datasets
- ✅ AI-powered classification (HOT/WARM/COLD)
- ✅ Cost calculation and optimization
- ✅ JWT authentication
- ✅ RESTful API with Swagger documentation
- ✅ Database persistence
- ✅ Error handling and logging

### Frontend
- ✅ Beautiful Material-UI dashboard
- ✅ Real-time data visualization
- ✅ Interactive charts and analytics
- ✅ Cloud provider management
- ✅ Data migration interface
- ✅ Responsive design
- ✅ Real-time updates via WebSocket
- ✅ Dark/light theme support

### DevOps
- ✅ Docker containerization
- ✅ Docker Compose orchestration
- ✅ Kubernetes manifests
- ✅ Horizontal Pod Autoscaling
- ✅ Ingress configuration
- ✅ Health checks and monitoring

---

## 🎬 Demo

Watch the demo video to see CloudFlux AI in action:
- Real-time dashboard with live cloud data
- Multi-cloud integration showcase
- Data classification and cost analysis
- UI/UX walkthrough

**Demo Video:** See `cloudflux-ai/Demo-video.mp4`

---

**Last Updated:** November 10, 2025
**Version:** 1.0.0
**Status:** Production Ready ✅
